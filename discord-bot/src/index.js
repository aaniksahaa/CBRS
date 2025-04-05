const { Client, GatewayIntentBits } = require('discord.js') ;

require('dotenv').config()

const client = new Client({ intents: [GatewayIntentBits.Guilds,GatewayIntentBits.MessageContent,GatewayIntentBits.GuildMembers,GatewayIntentBits.GuildMessages] });

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate',(message)=>{

    console.log("member: "+message.member+" message: "+message.content)

    if(message.author.bot) return;

    if(message.content==="hello"){
        message.reply("hello")
    }


})


client.on('interactionCreate',(interaction)=>{

    if(!interaction.isChatInputCommand()) return ;

    if(interaction.commandName=== "hey"){
      interaction.reply("thanks for calling me, how can I help");
    }
});


client.login(process.env.TOKEN);