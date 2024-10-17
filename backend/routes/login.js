const router = require('express').Router()
const { body, validationResult } = require('express-validator')
const { getToken } = require('../controllers/login')

router.post('/', [
    body('username').notEmpty(),
    body('password').notEmpty()
], async (req, res, next) => {
    console.log(req.body)
    const result = validationResult(req)
    if(result.isEmpty() === false) {
        return res.send({errors: result.array()})
    }
    
    try {
        const login_response = await getToken(req.body)
        res.json(login_response)
    }
    catch(err) {
        console.log(err)
        next(err)
    }
});

module.exports = router;