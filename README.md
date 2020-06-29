# twitter-exporter
for Balaji S Srinivasan

This is my submission to the Twitter Exporter contest.

I worked with a partner. Together we completed both the requirement for a local app and a hosted web site.

First, some features about the local app, which uses the "Mass DM" approach:

- Followers are ranked and prioritized by account size.
- You can close the app at anytime without losing track of who has already been messaged. The code picks up right where it left off using a .txt file as a database.
- Approximately every 2 hours of running the app, the user receives a message with the expected remaining runtime.
- The app sends 950 DMs per day, leaving its user with room to chat with friends. This can be adjusted to 990 or even 1000 DMs per day to truly optimize the length of time it takes to message all followers.
- While it has a simple UI (runs in command prompt), it should satisfy the needs of any user looking to contact all their followers.
- There is basic confirmation that the right message has been entered.

Here is an image of me using the compiled .exe file:

https://i.imgur.com/2FO15Ba.png

The script used to make the .exe and the .exe itself can be found here:

https://github.com/plutownium/twitter-exporter/tree/master

For our hosted website, we have additional features:

We analyze your followers to make your efforts count. We know what followers have the largest social media footprint, which are most loyal to you, and can help you leverage this inormation to build your brand. By targeting your most prominent "cadets" with give aways or exclusive material, you can make them more likely to give you exposure with mentions or retweets. By giving your loyal influencers access to insider information, you can reward them for sticking by your side and help them better represent you. Finally, you can DM the masses to keep them informed of whatever you want.

Our UI is rudimentary right now, but we have the backend to support advanced analytics to make your DMs count.

Here is a video using the client-side code for the website:

https://drive.google.com/file/d/15w7rIS0Zhh67yPT8rdbe47B2-Ha7U7Io/view

And this is the landing page followers will see when they click the included link:

https://cdn.discordapp.com/attachments/651923786903453702/722511234553085982/unknown.png
