require("dotenv").config();
const express = require("express");
console.log(process.env.TBO_CLIENT_ID)
const app = express();
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Travel Backend Running 🚀");
});



app.get("/auth", async (req, res) => {
  try {
    const response = await fetch(
      "http://Sharedapi.tektravels.com/SharedData.svc/rest/Authenticate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ClientId: process.env.TBO_CLIENT_ID,
          UserName: process.env.TBO_USERNAME,
          Password: process.env.TBO_PASSWORD,
          EndUserIp: process.env.TBO_IP
        })
      }
    );
 const text = await response.text();
   // const data = await response.json();
  //  console.log(data)
    res.send(text);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/search", async (req, res) => {
  try {
    const response = await fetch(
      "http://api.tektravels.com/BookingEngineService_Air/AirService.svc/rest/Search",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          EndUserIp: process.env.TBO_IP,
          TokenId: process.env.TBO_TOKEN,

          AdultCount: 2,
          ChildCount: 1,
          InfantCount: 0,

          DirectFlight: false,
          OneStopFlight: false,

          JourneyType: 1, // 1 = One Way

          PreferredAirlines: null,

         Segments: [
  {
    Origin: "DEL",
    Destination: "BLR",
    FlightCabinClass: 1,

    PreferredDepartureTime: "2026-03-01T00:00:00",
    PreferredArrivalTime: "2026-03-01T00:00:00"
  }
],

          Sources: null
        })
      }
    );

    const data = await response.json();
  const responseData = data.Response;


if (responseData.ResponseStatus !== 1) {
  return res.json({
    message: responseData.Error?.ErrorMessage || "No flights found"
  });
}

const results = responseData.Results || [];

const flights = [];

// Now safe to iterate
for (const trip of results) {
  for (const flight of trip) {

    const segment = flight.Segments[0][0];

    flights.push({
      airline: segment.Airline.AirlineName,
      flightNumber: `${segment.Airline.AirlineCode}-${segment.Airline.FlightNumber}`,

      from: segment.Origin.Airport.CityCode,
      to: segment.Destination.Airport.CityCode,

      departureTime: segment.Origin.DepTime,
      arrivalTime: segment.Destination.ArrTime,

      duration: segment.Duration,
      price: flight.Fare.PublishedFare,

      baggage: segment.Baggage,
      cabinBaggage: segment.CabinBaggage,

      seats: segment.NoOfSeatAvailable,
      refundable: flight.IsRefundable,

      resultIndex: flight.ResultIndex
    });
  }
}

res.json(flights);


  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});
