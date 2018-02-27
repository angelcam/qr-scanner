from qr_scanner.utils import cam_id_from_url


def test_cam_id_from_url():
    url1 = 'https://mjpeg1-eu3-3.angelcam.com/stream/preview_45005?token=eyJjYNTksInRpbWVvdXQiOjM2MDB9.76f04356f5d76278e348f77a'
    url2 = 'https://mjpeg1-eu3-3.angelcam.com/stream/preview_45005'
    url3 = 'https://e3-eu2.angelcam.com/m3-eu3/preview_40492/playlist.m3u8?token=eyk5MDI4ODMzOSwidGltZW91dCI6MzYwMH0=.3c923c520b6d'
    url4 = 'https://e3-eu2.angelcam.com/m3-eu3/preview_40492/playlist.m3u8'

    assert cam_id_from_url(url1) == 'preview_45005'
    assert cam_id_from_url(url2) == 'preview_45005'
    assert cam_id_from_url(url3) == 'preview_40492'
    assert cam_id_from_url(url4) == 'preview_40492'
