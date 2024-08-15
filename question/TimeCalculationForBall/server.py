
import random
import math

def generate():
    params = dict()
    correct_answers = dict()
    nDigits = 3
    sigfigs = 3
    data = dict(params=params, correct_answers=correct_answers, nDigits=nDigits, sigfigs=sigfigs)

    # Dynamic Parameter Selection
    # Randomly choose between SI and USCS units
    if random.choice(['SI', 'USCS']) == 'SI':
        unitsDist = 'meters'
        unitsSpeed = 'm/s'
        g = 9.81  # acceleration due to gravity in m/s^2
        H = random.uniform(10, 100)  # height in meters
        vx = random.uniform(5, 20)  # initial speed in m/s
    else:
        unitsDist = 'feet'
        unitsSpeed = 'ft/s'
        g = 32.2  # acceleration due to gravity in ft/s^2
        H = random.uniform(30, 300)  # height in feet
        vx = random.uniform(15, 65)  # initial speed in ft/s

    # Value Generation
    params['H'] = round(H, nDigits)
    params['vx'] = round(vx, nDigits)
    params['unitsDist'] = unitsDist
    params['unitsSpeed'] = unitsSpeed

    # Solution Synthesis
    t = math.sqrt(2 * H / g)  # time to reach the ground

    correct_answers['t'] = round(t, nDigits)

    return data

if __name__ == "__main__":
    # Example usage
    result = generate()
    print(result)
