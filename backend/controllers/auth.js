const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const jwt = require("jsonwebtoken");
const { createUser } = require("./user");

const admin = require("firebase-admin");
const serviceAccount = require("../cred/classaid-83cc6-firebase-adminsdk-mntiv-6443038a46.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const getTokenFromGoogleUid = async (payload) => {
  const { token } = payload;
  const decodedToken = await admin.auth().verifyIdToken(token);

  console.log(decodedToken);

  const existingUser = await prisma.user.findFirst({
    where: {
      google_uid: decodedToken.uid,
    },
  });

  let user = existingUser;

  if (user == null) {
    console.log("\n\nNew User, signing up...\n\n");

    const response = await createUser({
      username: decodedToken.email.split("@")[0],
      password: `<<REDACTED_GOOGLE_${decodedToken.uid}>>`,
      name: decodedToken.name,
      email: decodedToken.email,
      profile_picture_url: decodedToken.picture,
      google_uid: decodedToken.uid,
    });

    if (!response.success) {
      throw Error("Server Error");
    }

    user = response.user;
  }

  console.log(user);

  const accessToken = jwt.sign(user, process.env.SECRET);
  return { user: user, token: accessToken };
};

module.exports = { getTokenFromGoogleUid };
