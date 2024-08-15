
const math = require('mathjs');

const generate = () => {
    // Define unit systems and their corresponding units
    const units = {
        si: {
            dist: 'm',
            speed: 'm/s',
            acceleration: 9.81 // Acceleration due to gravity in m/s^2 (SI units)
        },
        uscs: {
            dist: 'ft',
            speed: 'ft/s',
            acceleration: 32.2 // Acceleration due to gravity in ft/s^2 (USCS units)
        }
    };

    // Randomly select a unit system
    const unitSystemKeys = Object.keys(units);
    const selectedUnitSystem = units[unitSystemKeys[math.randomInt(0, unitSystemKeys.length)]];

    // Generate a random height within a reasonable range
    const minHeight = 10; // Minimum height
    const maxHeight = 100; // Maximum height
    const H = math.randomInt(minHeight, maxHeight);

    // Generate a random initial horizontal speed within a reasonable range
    const minSpeed = 5; // Minimum speed
    const maxSpeed = 50; // Maximum speed
    const vx = math.randomInt(minSpeed, maxSpeed);

    // Calculate the time to reach the ground using the kinematic equation
    // H = 0.5 * g * t^2 => t = sqrt(2 * H / g)
    const t = math.sqrt(2 * H / selectedUnitSystem.acceleration);

    // Return the generated data
    return {
        params: {
            H: H,
            vx: vx,
            unitsDist: selectedUnitSystem.dist,
            unitsSpeed: selectedUnitSystem.speed
        },
        correct_answers: {
            t: math.round(t, 3) // Round to 3 decimal places
        },
        nDigits: 3,  // Define the number of digits after the decimal place.
        sigfigs: 3   // Define the number of significant figures for the answer.
    };
};

module.exports = {
    generate
};
