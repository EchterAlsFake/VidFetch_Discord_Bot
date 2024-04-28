<div align = center>
<img src="https://github.com/EchterAlsFake/VidFetch_Discord_Bot/logo.png" alt="Discord Bot Logo" width="350"/>
<br>

# Vid Fetch Discord Bot


---

**[<kbd><strong>&nbsp;<br>&nbsp;Invite to your server&nbsp;<br>&nbsp;</strong></kbd>](https://discord.com/oauth2/authorize?client_id=1093631510428516434&scope=applications.commands)** 

---
</div>

# Table of contents
- [Description](#description)
- [Features](#features)
- [Bot commands](#bot-commands)
- [Requirements](#requirements)
- [Open Source Information](#open-source-information)
- [Hosting](#hosting)
- [License](#license)

# Description

Vid Fetch Discord Bot is a discord bot made for
downloading music videos
<br> from YouTube and sending them back to the user. The Bot can download
<br> a single video or a whole YouTube playlist with integrated threading support.

# Features:

- Downloading a video
- m4a codec support
- Download a whole playlist
- Get a direct download link for videos
- Integrated threading for faster download
- Intuitive application commands

# Bot commands

| Command          | Description                                                   | Arguments                                                                                                                                                                              | Options       |
|------------------|---------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `/download`      | Downloads a video and uploads it to you as .m4a file          | `url`: The video url from YouTube.com                                                                                                                                                  | |
| `/playlist`      | Same as /download but for every video in a YT playlist        | `url`: The playlist url from YouTube.com                                                                                                                                               |  |
| `/get_direct_link` | Gives the link of the download source (Supports up to 8K res) | `url`: The video url from YouTube.com <br> `video`: Download / get video <br>`music`: Download / get music  <br>`highest_resolution`: Go over 720p resolution, but has no music in it. | `True`: Yes<br>`False`: No |
| `/help`          | Prints a little help message                                  |                                                                                                                                                                                        |               |
| `/credits`       | Credits for all used things in this application               |                                                                                                                                                                                        |               |

# Requirements

- The downloaded music video MUST NOT exceed 8MB size
- The video MUST NOT be blocked in Germany
- You need to have private DMs from server members enabled in your DC

# Open Source information

The code here is exactly the same, which is running in the background,
<br>when you use it. 
I need to keep the background running application closed,
<br>to prevent leaking the API key.
If you don't trust me, you can easily copy
<br> all of my code, create your own bot on the discord developer portal and use your
<br>own API key :) 
# Hosting

I have no resources to buy a hosting server for the bot.
<br>In the past I had my old laptop for hosting, but it died
<br> sometimes I can host the bot from my main PC or my phone but
<br>that are unstable methods.

# BUT 

You can host it by yourself with one click!
<br>Go [here](https://github.com/EchterAlsFake/VidFetch_Discord_Bot/releases)
<br>Select the version for either Linux or Windows
<br>Run it :) 


# License

GNU GENERAL PUBLIC LICENSE v3 2007
<br>Copyright (c) 2023 EchterAlsFake | Johannes Habel

[License](https://www.gnu.org/licenses/gpl-3.0.en.html)
