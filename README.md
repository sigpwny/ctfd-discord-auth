# CTFd discord auth

Adds a /discordauth discord oauth endpoint to CTFd, which sends a message to a specified webhook on successful authentication

useful for verifying discord user <-> ctfd user


setup:

1. clone to ctfd plugins folder
2. register discord application https://discord.com/developers/applications
3. get oauth client id, client secret
5. add redirect uri: `$ctf_url/discordauth` e.g. `https://2022.uiuc.tf/discordauth`.
   Go to your Discord Developer Protol, click on the new application, click "Oath2" on the left hand bar, and add a "Redirect" with the uri above.
7. create webhook in discord
8. set appropriate env vars for ctfd: DISCORD_AUTH_WEBHOOK, DISCORD_AUTH_CLIENT_ID, DISCORD_AUTH_SECRET
  - preferred: in docker-compose.yml
