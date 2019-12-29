from tobrot.helper_funcs.display_progress import progress_for_pyrogram, humanbytes
from tobrot.helper_funcs.help_Nekmo_ffmpeg import take_screen_shot
from tobrot.helper_funcs.split_large_files import split_large_files
from tobrot.helper_funcs.copy_similar_file import copy_file

from tobrot import (
    TG_MAX_FILE_SIZE,
    EDIT_SLEEP_TIME_OUT
    EDIT_SLEEP_TIME_OUT,
    DOWNLOAD_LOCATION
)


@@ -92,17 +94,33 @@
                    dict_contatining_uploaded_files
                )
        else:
            sent_message = await upload_single_file(message, local_file_name, caption_str)
            sent_message = await upload_single_file(
                message,
                local_file_name,
                caption_str,
                from_user
            )
            if sent_message is not None:
                dict_contatining_uploaded_files[os.path.basename(local_file_name)] = sent_message.message_id
    return dict_contatining_uploaded_files


async def upload_single_file(message, local_file_name, caption_str):
async def upload_single_file(message, local_file_name, caption_str, from_user):
    await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
    sent_message = None
    start_time = time.time()
    #
    thumbnail_location = os.path.join(
        DOWNLOAD_LOCATION,
        "thumbnails",
        str(from_user) + ".jpg"
    )
    LOGGER.info(thumbnail_location)
    #
    try:
        message_for_progress_display = await message.reply_text(
            "starting upload of {}".format(os.path.basename(local_file_name))
        )
        if local_file_name.upper().endswith(("MKV", "MP4", "WEBM")):
            metadata = extractMetadata(createParser(local_file_name))
            duration = 0
@@ -111,32 +129,39 @@
            #
            width = 0
            height = 0
            thumb_image_path = await take_screen_shot(
                local_file_name,
                os.path.dirname(os.path.abspath(local_file_name)),
                (duration / 2)
            )
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert(
                    "RGB"
                ).save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            thumb_image_path = None
            if os.path.exists(thumbnail_location):
                thumb_image_path = await copy_file(
                    thumbnail_location,
                    os.path.dirname(os.path.abspath(local_file_name))
                )
            else:
                thumb_image_path = await take_screen_shot(
                    local_file_name,
                    os.path.dirname(os.path.abspath(local_file_name)),
                    (duration / 2)
                )
                # get the correct width, height, and duration for videos greater than 10MB
                if os.path.exists(thumb_image_path):
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    # resize image
                    # ref: https://t.me/PyrogramChat/44663
                    # https://stackoverflow.com/a/21669827/4723940
                    Image.open(thumb_image_path).convert(
                        "RGB"
                    ).save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    # https://stackoverflow.com/a/37631799/4723940
                    img.resize((320, height))
                    img.save(thumb_image_path, "JPEG")
                    # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            #
            thumb = None
            if os.path.exists(thumb_image_path):
            if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                thumb = thumb_image_path
            # send video
            sent_message = await message.reply_video(
@@ -154,11 +179,12 @@
                progress=progress_for_pyrogram,
                progress_args=(
                    "trying to upload",
                    message,
                    message_for_progress_display,
                    start_time
                )
            )
            os.remove(thumb)
            if thumb is not None:
                os.remove(thumb)
        elif local_file_name.upper().endswith(("MP3", "M4A", "M4B", "FLAC", "WAV")):
            metadata = extractMetadata(createParser(local_file_name))
            duration = 0
@@ -170,6 +196,15 @@
                title = metadata.get("title")
            if metadata.has("artist"):
                artist = metadata.get("artist")
            thumb_image_path = None
            if os.path.isfile(thumbnail_location):
                thumb_image_path = await copy_file(
                    thumbnail_location,
                    os.path.dirname(os.path.abspath(local_file_name))
                )
            thumb = None
            if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                thumb = thumb_image_path
            # send audio
            sent_message = await message.reply_audio(
                audio=local_file_name,
@@ -179,36 +214,52 @@
                duration=duration,
                performer=artist,
                title=title,
                # thumb=,
                thumb=thumb,
                disable_notification=True,
                reply_to_message_id=message.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    "trying to upload",
                    message,
                    message_for_progress_display,
                    start_time
                )
            )
            if thumb is not None:
                os.remove(thumb)
        else:
            thumb_image_path = None
            if os.path.isfile(thumbnail_location):
                thumb_image_path = await copy_file(
                    thumbnail_location,
                    os.path.dirname(os.path.abspath(local_file_name))
                )
            # if a file, don't upload "thumb"
            # this "diff" is a major derp -_- 😔😭😭
            thumb = None
            if thumb_image_path is not None and os.path.isfile(thumb_image_path):
                thumb = thumb_image_path
            #
            # send document
            sent_message = await message.reply_document(
                document=local_file_name,
                # quote=True,
                # thumb=,
                thumb=thumb,
                caption=caption_str,
                parse_mode="html",
                disable_notification=True,
                reply_to_message_id=message.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    "trying to upload",
                    message,
                    message_for_progress_display,
                    start_time
                )
            )
            if thumb is not None:
                os.remove(thumb)
    except Exception as e:
        await message.edit_text("**FAILED**\n" + str(e))
        await message_for_progress_display.edit_text("**FAILED**\n" + str(e))
    else:
        await message.delete()
        await message_for_progress_display.delete()
    os.remove(local_file_name)
    return sent_message
