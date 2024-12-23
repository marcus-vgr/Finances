# Finances

Simple application to keep track of your expenses per month. Its use should be absolutely straightforward.

The only requirement to use it is having `python3` installed in your machine. Once getting the repository via ```git clone https://github.com/marcus-vgr/Finances.git```, all the setup is installed by simply ```source install.sh``` in the main repository directory. 

To run the application after installation just type in your terminal ```./run.sh```.


## Telegram Bot

This application supports Telegram Bot, so you can add expenses to the database without having to be on your computer. To do it, in your Telegram app first search for ```BotFather``` and type ```\start``` followed by ```\newbot``` to create a new bot. Follow the prompts.

BotFather will generate an **API Token**. Save this token in a file called ```.tokenTelegram``` inside the main repo directory.

Your telegram bot identifies queries of the following type:
```
DD/MM/YYYY ; VALUE ; CATEGORY ; DESCRIPTION
```
with `CATEGORY` having to be one of the availables in the application, as you see in the UI. You don't have to worry about case when writting. It is just mandatory to use `;` as a separator in your query. 
```
One query per message!
```

### Running the bot

When in your computer, if you want you can process the latest messages you sent to your bot by running 
```
python main.py --method bot
```
assuming you have already setup the python env. But far more convenient is using ```cron``` to schedule the job to run e.g. every 6 hours. 
To do it, just type in your terminal ```crontab -e``` and add the following line:
```
0 */6 * * * /path/to/repo/Finances/FinancesEnv/bin/python /path/to/repo/Finances/main.py --method bot
```

PS: `cron` is available in Linux/MacOS. If you are using Windows, you can try `Windows Task Scheduler`, but I haven't tested it.
