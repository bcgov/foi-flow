/**
 *
 * Run from any directory with:
 *   node forms-flow-web/scripts/tests/foimod-5410-correspondence-subject.test.cjs
 *
 * The helper is a plain ES module but forms-flow-web is not configured with
 * "type": "module". Loading the source through a data URL executes the real
 * exported helper without changing application or test-runner configuration.
 */
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');

const sourcePath = path.resolve(
  __dirname,
  '../../src/components/FOI/customComponents/ContactApplicant/helper.js'
);
const source = readFileSync(sourcePath, 'utf8');
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source, 'utf8').toString('base64')}`;

// Run against the actual helper code, not a copy of its implementation.
test('FOIMOD-5410: historical correspondence subject fallback', async (t) => {
  const { getCorrespondenceSubject } = await import(moduleUrl);
  const activeList = [{ fileName: 'ActiveLetter', templateName: 'Current Letter' }];

  await t.test('keeps an explicit saved subject', () => {
    assert.equal(
      getCorrespondenceSubject(
        { correspondencesubject: 'Saved subject', templatename: 'RetiredLetter' },
        activeList,
        '123'
      ),
      'Saved subject'
    );
  });

  await t.test('resolves display names for active templates', () => {
    assert.equal(
      getCorrespondenceSubject({ templatename: 'ActiveLetter' }, activeList, '123'),
      'Current Letter'
    );
  });

  await t.test('uses the stored filename for retired templates', () => {
    const actual = getCorrespondenceSubject({ templatename: 'RetiredLetter' }, activeList, '123');
    assert.equal(actual, 'RetiredLetter');
    assert.equal(actual.toLowerCase(), 'retiredletter');
    assert.equal(actual.replaceAll(/[^a-zA-Z0-9_\-]/g, ''), 'RetiredLetter');
  });

  await t.test('handles an unavailable template list', () => {
    assert.equal(
      getCorrespondenceSubject({ templatename: 'RetiredLetter' }, undefined, '123'),
      'RetiredLetter'
    );
  });
});
