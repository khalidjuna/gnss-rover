import dropbox

# Dropbox access token (yang Anda miliki)
access_token = "sl.u.AF39ujNQ2-7XwQjo5VYQiVlC56i4urIO6iF0SQ3zQd7578Ub1cWz6SuXfGtN1DICaDQ4GE_18_J31pD4lT1h4UBsRlBu35mCeMrBqBMq1kwTS3NDyfZQ8c9Jyh7_itcoscskjNltwkY9xeeOSKt-wXVohLyXepryyPEmC9KFQvtDlRzeXyPd8AkdLdbIyUhr6u2ldPPEkIAI4xuhk19JlP1C4wGe9gh_Ew6WHPd9aQEqNEqmx_-ntEIvc3D0sxb0uFs0xqLy2COUl8iBdZeLXty--WFdbppcVMT9N6sUq3PHJ-YZB7lD4L9hIlBPsSbeNiJ56tJIEiaguiLUIIhgk1jV4jE7AyE2tohpy441U3FLGovwx3CTnvsi7NILfTeslXC0wWhJmNcK5irILuDcWH38udYiGGwSxCt0YP8XCFYXvOyTGZ9fbCcC3iwFGB5m2PvVaoCbSXwJxiVlgfAJrVEdEJXPJ0Q2dKTTRwDyEy-B-ofeNbv7clXZoj6ydRXZ9ntO4ROUV-UNEWWv6M1qoxHIGq0pCh_L_T7urd_UAZ1_KAi-w114VssWDL2SsdtP4kBeyDfDm88ubxBvUryZZZ7PD7K_4DmBhujTHyX_JxLi-_4yuwGiemkAMIv1ZKnMcCuaZG_5xLaAzfNpZrUUE4kaVOCQm0h8NNuRw4dhncmdWkTqpsqPzKUe1gMu-HBo12vc7OlLsCYj4MH5Gn3Gfxan6dRk5g8o5B4CpAnYDoUuWqGEMkhJIuf9nnRKzxVgqpKT4fhwVgumGbYzSbeqs2D4QDx3R10ZHBhm2XNIlDfOOUN_OKIyTzbXfB1k6wKGrJBFSD8fRB9aPF7RIwWHUXLfBCouB8JgJzn8YrmBzUJOyaFONplbqBxy1Sh9Qj1UFVap5vlwQvwPS94oaDLWFfRp03jEV_rD8SxHOx957TuXyUCPQ58puomuh_jYEBOl06wsK2G9wOcqY6LgfrDI4boGiPGX8eQ2tgaE2z-vntLfmJJC6RusenPHMeZRXdcRg4I1pGWM2SGQGLkhgIiOEVOf5sV0af6C4K8ZYJ4eGnFKcbW21dbFW657A3WLD_zG27e_hH1F0LpiKqpnD4YbWzQR2D-Ez7M3lm-U9XK0UYGAES4HiSWhECAYDYYCmpCPfq43xyBPiFKMBtpX4doC9qrO57UEXQbSuvXIaZxMmZoQToDWOSV0EpWC8LJwjks9PhhwOdr8jU5dD7zzfWMFUUhHFpNUGrt2LB2MlQ1JTFKYYLudWf1pnWqjD-ryHUF81UCIbHuO-SVX8XvCkkuAni_O5x-C04YlXBio3a-fePHEm9XJJP_NcSwoYzvYmfJff3lmFxQLIoXkHMjgF590qdk7VJr--fcXZPpAmZu6Rb7656MQ1N2AYRa66rrLawaqGjVmfLBQ4bmi0OeaSktFqqQt"

# Function to upload a file to Dropbox
def upload_file_to_dropbox(file_path, dropbox_path, access_token):
    dbx = dropbox.Dropbox(access_token)
    try:
        with open(file_path, "rb") as file:
            dbx.files_upload(
                file.read(),
                dropbox_path,
                mode=dropbox.files.WriteMode("overwrite")
            )
        print(f"File '{file_path}' uploaded successfully to {dropbox_path}")
    except Exception as e:
        print(f"Error uploading file: {e}")

# Main script to upload .obs and .nav files
def main():
    # Specify the local file paths
    local_file_path_obs = "../output1.obs"
    local_file_path_nav = "../output1.nav"

    # Specify the Dropbox paths where you want to upload the files
    dropbox_path_obs = "/GPS ZED-F9P/Rover/file.obs"
    dropbox_path_nav = "/GPS ZED-F9P/Rover/file.nav"

    # Upload the files to Dropbox
    upload_file_to_dropbox(local_file_path_obs, dropbox_path_obs, access_token)
    upload_file_to_dropbox(local_file_path_nav, dropbox_path_nav, access_token)

# Run the main function
if __name__ == "__main__":
    main()
