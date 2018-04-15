#!/usr/bin/env node
const fs = require("fs")
const process = require("process")

const { argv } = process

if (argv.length === 2) { // No arguments passed
    console.error("You must pass service type as argument")

    process.exit(1)
}

const service = Array.from(argv).pop()

const path = "./" + service

if (!(fs.existsSync(path) && fs.statSync(path).isDirectory())) {
    console.error("Unknown service")

    process.exit(1)
}

const cAdvisorPath = path + "/cadvisor.json"

if (!(fs.existsSync(cAdvisorPath) && fs.statSync(cAdvisorPath).isFile())) {
    console.error("Problem with cAdvisor JSON file")

    process.exit(1)
}

const cAdvisorJSON = require(cAdvisorPath)

const container = Object.keys(cAdvisorJSON).shift()

const { stats } = cAdvisorJSON[container]

let previous = null
let startTime = null

const cpu_in_time = stats.map(stat => {
    let cpuUsage = null

    const { cpu, timestamp } = stat

    const total = cpu.usage.total

    const time = new Date(timestamp).getTime()
    
    if (!startTime) {
        startTime = time
    }

    if (!!previous) {
        cpuUsage = (total - previous) / 1000000000 // Don't ask why
    }

    previous = total

    if (!!cpuUsage) {
        return { cpuUsage, cpuUsageInPercentage: cpuUsage * 100, time: time - startTime }
    }
}).filter(field => !!field)

cpu_in_time.unshift({
    time: "time", 
    cpuUsage: "cpu_usage",
    cpuUsageInPercentage: "cpu_usage_in_%"
})

fs.writeFile(path + "/cadvisor.csv", cpu_in_time.map(field => field.time + ";" + field.cpuUsage.toString().replace(".", ",") + ";" + field.cpuUsageInPercentage.toString().replace(".", ",")).join("\n"), error => {
    if (error) {
        throw error
    }

    console.log("Report was generated")
})

