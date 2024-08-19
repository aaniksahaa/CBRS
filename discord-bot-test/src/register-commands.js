const {REST,Routes,ApplicationCommandOptionType} = require('discord.js')
require('dotenv').config();

const commands = [
    {
        name: "hey",
        description: "Replies with hey"
    },
    {
        name: "add",
        description: "Adds two numbers" ,
        options: [
            {
                name:"first-number",
                description:"first number to add",
                type: ApplicationCommandOptionType.Number,
                required: true
            },
            {
                name:"second-number",
                description:"second number to add",
                type: ApplicationCommandOptionType.Number,
                required: true
            }
        ]
    }, 

    {
        name: "blood",
        description: "provide blood information",
        options:[
            {
                name: "blood-group",
                description: "patient's blood group",
                type: ApplicationCommandOptionType.String,
                choices: [
                    {
                        name: "O+ve" ,
                        value: "O+"
                    },
                    {
                        name: "O-ve" ,
                        value: "O-"
                    },
                    {
                        name: "A+ve" ,
                        value: "A+"
                    },
                    {
                        name: "A-ve" ,
                        value: "A-"
                    }
                    
                ],
                required:true
            },
            {
                name: "amount",
                description:"amount of blood needed(bags)",
                type: ApplicationCommandOptionType.Number,
                required:true
            },
            {
                name: "location",
                description: "Location of the hospital",
                type: ApplicationCommandOptionType.String,
                required:true
            },
            {
                name: "contact",
                description:"Contact Number of the seeker",
                type: ApplicationCommandOptionType.String,
                required:true
            },

            {
                name: "disease",
                description: "Patient's disease",
                type: ApplicationCommandOptionType.String
            }

        ]
    }
] ;


const rest = new REST({version:'10'}).setToken(process.env.TOKEN);

(async ()=>{

    try {

        console.log("registering slash commands...");
        
        await rest.put(
            Routes.applicationGuildCommands(process.env.CLIENT_ID,process.env.GUILD_ID),
            {body:commands} 
        ) ;

        console.log("registered slash commands successfully...");
    } catch (error) {
        console.error(error);
    }
})();