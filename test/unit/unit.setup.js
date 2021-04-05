import 'jest-extended'
import moment from 'moment-timezone'

import expressions from '@/data/en.json'

jest.setTimeout(60000)

global.date = {
  time_zone: moment.tz.guess()
}

global.audio = {
  base_64_webm_blob: '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'
}

global.enExpressions = expressions

process.env.LEON_LANG = 'en-US'
process.env.LEON_HOST = 'http://localhost'
process.env.LEON_PORT = 1338
process.env.LEON_TIME_ZONE = global.date.time_zone
process.env.LEON_TTS = true.toString()
process.env.LEON_TTS_PROVIDER = 'flite'
