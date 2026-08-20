#!/usr/bin/env node
// Execute the public JavaScript used by KASI's official sunrise/sunset page.

const crypto = require('crypto');
const https = require('https');
const vm = require('vm');

const SOURCES = {
  algorithms: 'https://astro.kasi.re.kr/resources/js/life/algorithms.js',
  delta_t: 'https://astro.kasi.re.kr/resources/js/life/delta_t.js',
};
const CALCULATOR_URL = 'https://astro.kasi.re.kr/life/pageView/9';

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function source(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        response.resume();
        source(response.headers.location).then(resolve, reject);
        return;
      }
      if (response.statusCode !== 200) {
        reject(new Error(`KASI source fetch failed: ${response.statusCode} ${url}`));
        response.resume();
        return;
      }
      const chunks = [];
      response.on('data', (chunk) => chunks.push(chunk));
      response.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    }).on('error', reject);
  });
}

function hhmm(value) {
  return `${String(value[0]).padStart(2, '0')}:${String(value[1]).padStart(2, '0')}`;
}

function calculate(api, item) {
  const parts = item.date.split('-').map(Number);
  const year = parts[0];
  const month = parts[1];
  const day = parts[2];
  const longitude = Number(item.longitude);
  const latitude = Number(item.latitude);
  const deltaT = api.getCurrentDeltaT(year);
  const jd = api.date2jd(year, month, day, 0, 0, 0);
  const sidereal = api.get_apparent_siderial_time(jd, deltaT);
  const sunRa = api.get_geocentric_sun_ra(jd, deltaT);
  const sunDec = api.get_geocentric_sun_dec(jd, deltaT);
  const base = api.limit_deg((sunRa - longitude - sidereal) / 360.0, 1.0);

  function boundary(altitude) {
    const y = Math.sin(api.deg2rad(altitude))
      - Math.sin(api.deg2rad(latitude)) * Math.sin(api.deg2rad(sunDec));
    const x = Math.cos(api.deg2rad(latitude)) * Math.cos(api.deg2rad(sunDec));
    const hourAngle = api.limit_deg(api.rad2deg(Math.acos(y / x)), 180.0);
    let morning = api.limit_deg(base - hourAngle / 360.0, 1.0) * 24.0 + 9.0;
    if (morning > 24.0) morning -= 24.0;
    const evening = api.limit_deg(base + hourAngle / 360.0, 1.0) * 24.0 + 9.0;
    return [api.hr2hr(morning), api.hr2hr(evening)];
  }

  const solar = boundary(-0.8333);
  const civil = boundary(-6.0);
  return {
    episode_id: item.episode_id,
    values: {
      sunrise: hhmm(solar[0]),
      sunset: hhmm(solar[1]),
      civil_morning: hhmm(civil[0]),
      civil_evening: hhmm(civil[1]),
    },
  };
}

let stdin = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { stdin += chunk; });
process.stdin.on('end', async () => {
  try {
    const input = JSON.parse(stdin);
    const texts = {};
    for (const name of Object.keys(SOURCES)) texts[name] = await source(SOURCES[name]);
    const sandbox = {Math, Date};
    vm.createContext(sandbox);
    for (const name of Object.keys(texts)) vm.runInContext(texts[name], sandbox, {filename: SOURCES[name]});
    const required = [
      'getCurrentDeltaT', 'date2jd', 'get_apparent_siderial_time',
      'get_geocentric_sun_ra', 'get_geocentric_sun_dec', 'deg2rad',
      'rad2deg', 'limit_deg', 'hr2hr',
    ];
    for (const name of required) {
      if (typeof sandbox[name] !== 'function') throw new Error(`KASI function unavailable: ${name}`);
    }
    const sourceHashes = {};
    for (const name of Object.keys(texts)) sourceHashes[name] = sha256(texts[name]);
    process.stdout.write(JSON.stringify({
      provider: 'Korea Astronomy and Space Science Institute (KASI)',
      calculator_url: CALCULATOR_URL,
      source_urls: SOURCES,
      source_sha256: sourceHashes,
      rows: input.map((item) => calculate(sandbox, item)),
    }));
  } catch (error) {
    process.stderr.write(`${error.stack || error}\n`);
    process.exitCode = 1;
  }
});
