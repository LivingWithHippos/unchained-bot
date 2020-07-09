from telegram import InlineKeyboardMarkup, InlineKeyboardButton as Button

from torrents.constants import UNRESTRICT_TORRENT


# torrent scheme:
# {
#         "id": "string",
#         "filename": "string",
#         "hash": "string", // SHA1 Hash of the torrent
#         "bytes": int, // Size of selected files only
#         "host": "string", // Host main domain
#         "split": int, // Split size of links
#         "progress": int, // Possible values: 0 to 100
#         // Current status of the torrent: magnet_error, magnet_conversion,
#         waiting_files_selection, queued, downloading, downloaded, error, virus, compressing, uploading, dead
#         "status": "downloaded",
#         "added": "string", // jsonDate
#         "links": [
#             "string" // Host URL
#         ]
def torrent_keyboard(torrent):
    buttons = [
        Button(torrent["filename"])
    ]

    if torrent["status"] == "downloaded":
        butt = [
            Button("Status: Ready"),
            Button("Unrestrict", callback_data=UNRESTRICT_TORRENT)
        ]
    else:
        butt = [
            Button("Status: {}".format(torrent["status"])),
            Button("Progress: {}".format(torrent["progress"]))
        ]

    buttons.append(butt)

    return InlineKeyboardMarkup(buttons)
