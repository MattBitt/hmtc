import os
import subprocess
import time

import yt_dlp
from configs import cnf
from my_logging import logger

# list of "all" yt-dlp options:
# found at https://stackoverflow.com/questions/26495953/youtube-dl-python-library-documentation
# ydl_opts = {
#         'usenetrc': opts.usenetrc,
#         'username': opts.username,
#         'password': opts.password,
#         'twofactor': opts.twofactor,
#         'videopassword': opts.videopassword,
#         'ap_mso': opts.ap_mso,
#         'ap_username': opts.ap_username,
#         'ap_password': opts.ap_password,
#         'quiet': (opts.quiet or any_getting or any_printing),
#         'no_warnings': opts.no_warnings,
#         'forceurl': opts.geturl,
#         'forcetitle': opts.gettitle,
#         'forceid': opts.getid,
#         'forcethumbnail': opts.getthumbnail,
#         'forcedescription': opts.getdescription,
#         'forceduration': opts.getduration,
#         'forcefilename': opts.getfilename,
#         'forceformat': opts.getformat,
#         'forcejson': opts.dumpjson or opts.print_json,
#         'dump_single_json': opts.dump_single_json,
#         'simulate': opts.simulate or any_getting,
#         'skip_download': opts.skip_download,
#         'format': opts.format,
#         'listformats': opts.listformats,
#         'outtmpl': outtmpl,
#         'outtmpl_na_placeholder': opts.outtmpl_na_placeholder,
#         'autonumber_size': opts.autonumber_size,
#         'autonumber_start': opts.autonumber_start,
#         'restrictfilenames': opts.restrictfilenames,
#         'ignoreerrors': opts.ignoreerrors,
#         'force_generic_extractor': opts.force_generic_extractor,
#         'ratelimit': opts.ratelimit,
#         'nooverwrites': opts.nooverwrites,
#         'retries': opts.retries,
#         'fragment_retries': opts.fragment_retries,
#         'skip_unavailable_fragments': opts.skip_unavailable_fragments,
#         'keep_fragments': opts.keep_fragments,
#         'buffersize': opts.buffersize,
#         'noresizebuffer': opts.noresizebuffer,
#         'http_chunk_size': opts.http_chunk_size,
#         'continuedl': opts.continue_dl,
#         'noprogress': opts.noprogress,
#         'progress_with_newline': opts.progress_with_newline,
#         'playliststart': opts.playliststart,
#         'playlistend': opts.playlistend,
#         'playlistreverse': opts.playlist_reverse,
#         'playlistrandom': opts.playlist_random,
#         'noplaylist': opts.noplaylist,
#         'logtostderr': opts.outtmpl == '-',
#         'consoletitle': opts.consoletitle,
#         'nopart': opts.nopart,
#         'updatetime': opts.updatetime,
#         'writedescription': opts.writedescription,
#         'writeannotations': opts.writeannotations,
#         'writeinfojson': opts.writeinfojson,
#         'writethumbnail': opts.writethumbnail,
#         'write_all_thumbnails': opts.write_all_thumbnails,
#         'writesubtitles': opts.writesubtitles,
#         'writeautomaticsub': opts.writeautomaticsub,
#         'allsubtitles': opts.allsubtitles,
#         'listsubtitles': opts.listsubtitles,
#         'subtitlesformat': opts.subtitlesformat,
#         'subtitleslangs': opts.subtitleslangs,
#         'matchtitle': decodeOption(opts.matchtitle),
#         'rejecttitle': decodeOption(opts.rejecttitle),
#         'max_downloads': opts.max_downloads,
#         'prefer_free_formats': opts.prefer_free_formats,
#         'verbose': opts.verbose,
#         'dump_intermediate_pages': opts.dump_intermediate_pages,
#         'write_pages': opts.write_pages,
#         'test': opts.test,
#         'keepvideo': opts.keepvideo,
#         'min_filesize': opts.min_filesize,
#         'max_filesize': opts.max_filesize,
#         'min_views': opts.min_views,
#         'max_views': opts.max_views,
#         'daterange': date,
#         'cachedir': opts.cachedir,
#         'youtube_print_sig_code': opts.youtube_print_sig_code,
#         'age_limit': opts.age_limit,
#         'download_archive': download_archive_fn,
#         'cookiefile': opts.cookiefile,
#         'nocheckcertificate': opts.no_check_certificate,
#         'prefer_insecure': opts.prefer_insecure,
#         'proxy': opts.proxy,
#         'socket_timeout': opts.socket_timeout,
#         'bidi_workaround': opts.bidi_workaround,
#         'debug_printtraffic': opts.debug_printtraffic,
#         'prefer_ffmpeg': opts.prefer_ffmpeg,
#         'include_ads': opts.include_ads,
#         'default_search': opts.default_search,
#         'youtube_include_dash_manifest': opts.youtube_include_dash_manifest,
#         'encoding': opts.encoding,
#         'extract_flat': opts.extract_flat,
#         'mark_watched': opts.mark_watched,
#         'merge_output_format': opts.merge_output_format,
#         'postprocessors': postprocessors,
#         'fixup': opts.fixup,
#         'source_address': opts.source_address,
#         'call_home': opts.call_home,
#         'sleep_interval': opts.sleep_interval,
#         'max_sleep_interval': opts.max_sleep_interval,
#         'external_downloader': opts.external_downloader,
#         'list_thumbnails': opts.list_thumbnails,
#         'playlist_items': opts.playlist_items,
#         'xattr_set_filesize': opts.xattr_set_filesize,
#         'match_filter': match_filter,
#         'no_color': opts.no_color,
#         'ffmpeg_location': opts.ffmpeg_location,
#         'hls_prefer_native': opts.hls_prefer_native,
#         'hls_use_mpegts': opts.hls_use_mpegts,
#         'external_downloader_args': external_downloader_args,
#         'postprocessor_args': postprocessor_args,
#         'cn_verification_proxy': opts.cn_verification_proxy,
#         'geo_verification_proxy': opts.geo_verification_proxy,
#         'config_location': opts.config_location,
#         'geo_bypass': opts.geo_bypass,
#         'geo_bypass_country': opts.geo_bypass_country,
#         'geo_bypass_ip_block': opts.geo_bypass_ip_block,
#         # just for deprecation check
#         'autonumber': opts.autonumber if opts.autonumber is True else None,
#         'usetitle': opts.usetitle if opts.usetitle is True else None,
#     }


class YouTubeLogger:
    def error(msg):
        logger.error(msg)

    def warning(msg):
        logger.warning(msg)

    def debug(msg):
        pass


# couldn't get this to work.  WAY TOO SLOW compared to subprocess function

# def get_collection_url_list(collection):
#     collection_videos = []
#     ydl_opts = {
#         "logger": YouTubeLogger,
#         # "quiet": True,
#         # "dump_single_json": True,
#         # "flat-playlist": True,
#         "skip_download": True,
#         # "download": False,
#         # "print_to_file": "config/collection_vids.txt",
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         try:
#             info = ydl.extract_info(collection["url"], download=True)
#         except yt_dlp.utils.ExtractorError:
#             logger.error("There was an error processing {} {}", info.returncode, url)
#     # with open(tmp_file, "w") as f:
#     for entry in info["entries"]:
#         collection_videos.append(entry["webpage_url"])
#     return collection_videos


def get_collection_url_list(collection):
    tmp_file = "playlist_videos.txt"
    args1 = ["yt-dlp"]
    args2 = []
    # if not cnf.LOG_LEVEL == "DEBUG":
    #     args2 = ["--no-warnings", "--quiet"]
    args3 = [
        "--flat-playlist",
        "-i",
        "--no-warnings",
        "--quiet",
        "--print-to-file",
        "url",
        tmp_file,
        collection["url"],
    ]
    yt_dl = subprocess.run(args1 + args2 + args3, stdout=subprocess.DEVNULL)
    with open(tmp_file) as f:
        lines = f.read().splitlines()
    os.remove(tmp_file)
    if yt_dl.returncode:
        logger.error("There was an error processing {}", yt_dl.returncode)
        return []
    else:
        logger.debug(
            "The URLs for collection {} were downloaded.", collection["collection_name"]
        )
        return lines


def get_json_info(url: str) -> dict:
    ydl_opts = {"writeinfojson": True, "skip_download": True, "logger": logger}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.ExtractorError:
            logger.error("Unable to download metadata for {}".format(url))

    return info


def download_files(url, file_name) -> bool:
    output_path = cnf.DOWNLOAD_PATH + file_name + ".%(ext)s"
    ydl_opts = {
        "logger": logger,
        "writedescription": True,
        "writethumbnail": True,
        "outtmpl": output_path,
        # "listformats": True,
        "format": "22",  # 22
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.ExtractorError:
            logger.error("There was an error processing {} {}", info.returncode, url)

    return True


if __name__ == "__main__":
    collection = {
        "collection_name": "XXXX",
        "url": "https://www.youtube.com/watch?v=7q1_ONJbu1w",
    }

    old_func_time = time.perf_counter()
    get_collection_url_list(collection)
    old_func_time = time.perf_counter() - old_func_time
    print(f"Old function time: {str(old_func_time)}")
