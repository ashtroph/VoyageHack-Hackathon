require("dotenv").config();

const express = require("express");
const fetch = require("node-fetch");
console.log(process.env.TBO_CLIENT_ID)
console.log(process.env.TBO_USERNAME)
console.log( process.env.TBO_PASSWORD)
console.log( process.env.TBO_IP)
const app = express();
app.use(express.json());

const PORT = process.env.PORT || 8080;

// 🔐 Function to get TBO Token
app.get("/tbo-auth", async (req, res) => {
  try {
    const response = await fetch(
      "https://api.tektravels.com/SharedServices/SharedData.svc/rest/Authenticate",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ClientId: process.env.TBO_CLIENT_ID,
          UserName: process.env.TBO_USERNAME,
          Password: process.env.TBO_PASSWORD,
          EndUserIp: process.env.TBO_IP,
        }),
      }
    );
    console.log(response)
     const text = await response.text();
      res.send(text);

    // ✅ Get RAW BODY as buffer (no parsing)
   

  } catch (err) {
    res.status(500).send(err.message);
  }
});

// 🟢 Health check
app.get("/", (req, res) => {
  res.send("TBO Auth Server Running 🚀");
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});