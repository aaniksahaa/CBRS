const { PrismaClient } = require('@prisma/client')
const prisma = new PrismaClient()

const getDemo = async (payload) => {
    //const data = await // database calls or other api calls here
    const user = await prisma.demo.create({
        data: { title: 'anik', name: 'saha', age: 2 },
    })
    //data = { 'data' : payload.data }
    data = user
    console.log(data)
    return data  
}

module.exports = {getDemo}
