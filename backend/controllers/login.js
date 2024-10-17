const jwt = require('jsonwebtoken');
const { getSingleUserByUsername } = require('./user');

const getToken = async (payload) => {
    console.log(payload)
    const user = await getSingleUserByUsername(payload)

    err = ''

    if(user == null)
    {
        err = 'Invalid Username';
        return {"message": err}
    }
    else if(user.password != payload.password)
    {
        err = 'Wrong Password';
        return {"message": err}
    }
    else 
    {
        const accessToken = jwt.sign(user, process.env.SECRET);
        return {"user": user, "token": accessToken}
    }
}

module.exports = {getToken}