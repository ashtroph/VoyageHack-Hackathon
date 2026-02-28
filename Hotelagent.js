require("dotenv").config();
const express = require("express");
console.log(process.env.TBO_USERNAME);
console.log(process.env.TBO_PASSWORD);
const app = express();
app.use(express.json());

const PORT = 8080;

app.get("/hotel-search", async (req, res) => {
  try {

    const auth = Buffer
      .from(`${process.env.TBO_USERNAME}:${process.env.TBO_PASSWORD}`)
      .toString("base64");

    const response = await fetch(
      "https://api.tbotechnology.in/TBOHolidays_HotelAPI/Search",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Basic ${auth}`
        },
        body: JSON.stringify({
          CheckIn: "2026-03-02",
          CheckOut: "2026-03-04",

          HotelCodes: "1247101",   // 🔥 sample code

          GuestNationality: "IN",

          PaxRooms: [
            {
              Adults: 2,
              Children: 0,
              ChildrenAges: []
            }
          ],

          ResponseTime: 23,
          IsDetailedResponse: false,

          Filters: {
            Refundable: false,
            NoOfRooms: 0,
            MealType: "All"
          }
        })
      }
    );

    const text = await response.text();
    console.log("Raw Response:", text);

    const data = JSON.parse(text);

    res.json(data);

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


app.listen(PORT, () => {
  console.log(`Server running on port ${PORT} 🚀`);
});