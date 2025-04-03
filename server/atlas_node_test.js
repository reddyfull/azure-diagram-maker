const { MongoClient, ServerApiVersion } = require('mongodb');

// Use the exact format from the example with the actual password
const password = "D69gYOJjIEsB4xnX";
const uri = `mongodb+srv://safine7374:${password}@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0`;

console.log("Connecting with URI: mongodb+srv://safine7374:****@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0");

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(uri, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});

async function run() {
  try {
    // Connect the client to the server
    console.log("Connecting to MongoDB Atlas...");
    await client.connect();
    
    // Send a ping to confirm a successful connection
    console.log("Sending ping command...");
    await client.db("admin").command({ ping: 1 });
    console.log("Pinged your deployment. You successfully connected to MongoDB!");
    
    // List databases
    console.log("\nListing databases:");
    const dbs = await client.db().admin().listDatabases();
    dbs.databases.forEach(db => {
      console.log(`- ${db.name}`);
    });
    
    // Create/access our database
    console.log("\nCreating/accessing azure_diagram_maker database");
    const db = client.db("azure_diagram_maker");
    
    // Create a test collection
    console.log("Creating test collection...");
    const testCollection = db.collection("test");
    
    // Insert a test document
    const testDoc = { name: "Test Document", value: "This is a test" };
    const result = await testCollection.insertOne(testDoc);
    console.log(`Inserted document with ID: ${result.insertedId}`);
    
    // Read it back
    const found = await testCollection.findOne({ name: "Test Document" });
    console.log(`Found document: ${JSON.stringify(found)}`);
    
  } finally {
    // Ensures that the client will close when you finish/error
    await client.close();
    console.log("Connection closed");
  }
}

run().catch(err => {
  console.error("Error connecting to MongoDB:", err);
  console.error("Error type:", err.constructor.name);
}); 