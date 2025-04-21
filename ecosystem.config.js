module.exports = {
  apps: [
    {
      name: "tor",
      script: "./tor-wrapper.sh",
      interpreter: "bash"
    },
    {
      name: "bot",
      script: "./car.py",
      interpreter: "python3"
    }
  ]
}
