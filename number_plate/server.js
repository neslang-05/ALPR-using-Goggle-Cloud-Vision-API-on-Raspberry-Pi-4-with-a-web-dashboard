const express = require("express");
const app = express();
const port = 3000;

const fs = require("fs");
const { exec } = require("child_process");
const path = require("path");
const userModel = require("./models/user");
const cookieParser = require("cookie-parser");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

app.set("view engine", "ejs");
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "public")));
app.use(cookieParser());

// Route to serve home route
app.get("/", (req, res) => {
  res.render("index");
});

// Route to serve main route
app.get("/main", isLoggedIn, async (req, res) => {
  let user = await userModel.findOne({ email: req.user.email });
  res.render("main");
});

// Route to serve learn
app.get("/learn", (req, res) => {
  res.render("learn");
});

app.get("/register", (req, res) => {
  res.render("register");
});

app.get("/login", (req, res) => {
  res.render("login");
});

app.post("/register", async (req, res) => {
  let { username, name, email, age, password } = req.body;
  let user = await userModel.findOne({ email });
  if (user) return res.status(500).send("user already registered");

  bcrypt.genSalt(10, (err, salt) => {
    bcrypt.hash(password, salt, async (err, hash) => {
      let user = await userModel.create({
        username,
        name,
        email,
        age,
        password: hash,
      });

      let token = jwt.sign({ email: email, userid: user._id }, "sshhhhh");
      res.cookie("token", token);
      res.redirect("main");
    });
  });
});

app.post("/login", async (req, res) => {
  let { email, password } = req.body;
  let user = await userModel.findOne({ email });
  if (!user) return res.status(500).send("something went wrong!");

  bcrypt.compare(password, user.password, function (err, result) {
    if (result) {
      let token = jwt.sign({ email: email, userid: user._id }, "sshhhhh");
      res.cookie("token", token);
      res.status(200).redirect("main");
    } else {
      res.redirect("/login");
      // console.log(result);
    }
  });
});

app.get("/logout", async (req, res) => {
  res.cookie("token", "");
  res.redirect("/login");
});

function isLoggedIn(req, res, next) {
  // Check if the token exists and is not an empty string
  const token = req.cookies.token;

  if (!token) {
    return res.redirect("/login"); // Redirect to login if token is missing or empty
  }

  try {
    // Verify the token
    let data = jwt.verify(token, "sshhhhh");
    req.user = data; // Attach the decoded data to the request object
    next(); // Proceed to the next middleware or route handler
  } catch (err) {
    // If JWT verification fails, redirect to the login page
    return res.redirect("/login");
  }
}

// Route to run the OCR script manually
app.post("/run-ocr", (req, res) => {
  const ocrScriptPath = path.join(__dirname, "ocr_script.py");

  exec(`python3 ${ocrScriptPath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing OCR script: ${error.message}`);
      return res.status(500).send("Error running OCR");
    }

    // Parse the output of your OCR script
    const ocrData = parseOCROutput(stdout);

    // Update license_plates.json with the parsed OCR data
    updateOCRResults(ocrData);

    res.json(ocrData);
  });
});

// Route to download CSV file
app.get("/csv", (req, res) => {
  const file = path.join(__dirname, "files", "license_plates.csv");
  res.download(file);
});
// Route to download JSON file
app.get("/json", (req, res) => {
  const file = path.join(__dirname, "files", "license_plates.json");
  res.download(file);
});

// Route to fetch CSV data
app.get("/csv-data", (req, res) => {
  const file = path.join(__dirname, "files", "license_plates.csv");
  fs.readFile(file, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading CSV file");
    }
    const rows = data
      .split("\n")
      .map((row) => {
        const [licensePlate, timestamp] = row.split(",");
        return { licensePlate, timestamp };
      })
      .filter((row) => row.licensePlate); // Filter out empty rows
    res.json(rows);
  });
});

// Route to get available slots
app.get("/slots", (req, res) => {
  const file = path.join(__dirname, "files", "license_plates.csv");
  fs.readFile(file, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading CSV file");
    }
    const rows = data.split("\n").filter((row) => row.trim() !== "").length;
    const totalSlots = 10;
    const availableSlots = totalSlots - rows;
    res.json({ availableSlots, totalSlots });
  });
});

// Serve images
app.get("/captured_image", (req, res) => {
  const file = path.join(__dirname, "files", "captured_image.jpg");
  res.sendFile(file);
});

app.get("/license_plate", (req, res) => {
  const file = path.join(__dirname, "files", "license_plate.jpg");
  res.sendFile(file);
});

// Route to fetch OCR results
app.get("/ocr-results", (req, res) => {
  const filePath = path.join(__dirname, "files", "license_plates.json");
  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading OCR results.");
    }
    try {
      const jsonData = JSON.parse(data);
      res.json(jsonData);
    } catch (error) {
      res.status(500).send("Error parsing JSON data.");
    }
  });
});

// Route to add a row to the data table
app.post("/add-row", (req, res) => {
  const { index, name, vehicleType } = req.body;
  const filePath = path.join(__dirname, "files", "data_table.json");

  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading data table.");
    }

    try {
      const jsonData = JSON.parse(data);
      const newRow = {
        licensePlate: jsonData[index].licensePlate,
        timestamp: jsonData[index].timestamp,
        name: name,
        vehicleType: vehicleType,
      };
      jsonData.splice(index, 0, newRow); // Insert at the correct position

      fs.writeFile(filePath, JSON.stringify(jsonData, null, 2), (writeErr) => {
        if (writeErr) {
          return res.status(500).send("Error updating data table.");
        }
        res.json({ message: "Row added successfully." });
      });
    } catch (error) {
      res.status(500).send("Error processing data table addition.");
    }
  });
});

// Route to delete a row from the data table
app.post("/delete-row", (req, res) => {
  const rowIndex = req.body.index;
  const filePath = path.join(__dirname, "files", "data_table.json");

  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading data table.");
    }

    try {
      const jsonData = JSON.parse(data);

      if (rowIndex >= 0 && rowIndex < jsonData.length) {
        jsonData.splice(rowIndex, 1);

        fs.writeFile(
          filePath,
          JSON.stringify(jsonData, null, 2),
          (writeErr) => {
            if (writeErr) {
              return res.status(500).send("Error updating data table.");
            }
            res.json({ message: "Row deleted successfully." });
          }
        );
      } else {
        res.status(400).send("Invalid row index.");
      }
    } catch (error) {
      res.status(500).send("Error processing data table deletion.");
    }
  });
});

// Route to fetch data for the data table
app.get("/data-table", (req, res) => {
  const filePath = path.join(__dirname, "files", "data_table.json");
  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading data table.");
    }
    try {
      const jsonData = JSON.parse(data);
      res.json(jsonData);
    } catch (error) {
      res.status(500).send("Error parsing JSON data.");
    }
  });
});

// Route to update an existing row in the data table
app.post("/update-row", (req, res) => {
  const { index, name, vehicleType } = req.body;
  const filePath = path.join(__dirname, "files", "data_table.json");

  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      return res.status(500).send("Error reading data table.");
    }
    try {
      const jsonData = JSON.parse(data);

      if (index >= 0 && index < jsonData.length) {
        jsonData[index].name = name;
        jsonData[index].vehicleType = vehicleType;

        fs.writeFile(
          filePath,
          JSON.stringify(jsonData, null, 2),
          (writeErr) => {
            if (writeErr) {
              return res.status(500).send("Error updating data table.");
            }
            res.json({ message: "Row updated successfully." });
          }
        );
      } else {
        res.status(400).send("Invalid row index.");
      }
    } catch (error) {
      res.status(500).send("Error processing data table update.");
    }
  });
});

// Function to parse OCR output
function parseOCROutput(output) {
  // Implement parsing logic based on your OCR script's output format
  return {}; // Example return value
}

// Function to update OCR results
function updateOCRResults(ocrData) {
  const filePath = path.join(__dirname, "files", "license_plates.json");
  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      console.error("Error reading OCR results:", err);
      return;
    }

    let jsonData = [];
    if (data) {
      try {
        jsonData = JSON.parse(data);
      } catch (error) {
        console.error("Error parsing JSON data:", error);
        return;
      }
    }

    jsonData.push(ocrData);

    fs.writeFile(filePath, JSON.stringify(jsonData, null, 2), (writeErr) => {
      if (writeErr) {
        console.error("Error updating OCR results:", writeErr);
      }
    });
  });
}

app.listen(port, () => {
  console.log(`App listening on port ${port}`);
});
