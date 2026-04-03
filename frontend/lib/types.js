/**
 * @typedef {Object} Coverage
 * @property {string} id
 * @property {string} workerId
 * @property {'active'|'inactive'|'suspended'} status
 * @property {number} weeklyPremium
 * @property {string[]} coverageTypes
 * @property {string} activeSince
 * @property {'low'|'medium'|'high'} disruptionLevel
 */

/**
 * @typedef {Object} Claim
 * @property {string} id
 * @property {string} workerId
 * @property {string} disruptionEventId
 * @property {'weather'|'pollution'|'restriction'} disruptionType
 * @property {'pending'|'approved'|'rejected'|'paid'} status
 * @property {number} amount
 * @property {string} submittedAt
 * @property {string} [processedAt]
 */

/**
 * @typedef {Object} DisruptionEvent
 * @property {string} id
 * @property {'weather'|'pollution'|'restriction'} type
 * @property {1|2|3|4|5} severity
 * @property {string} description
 * @property {string[]} affectedAreas
 * @property {number} affectedWorkers
 * @property {string} startTime
 * @property {string} [endTime]
 * @property {'active'|'resolved'} status
 */

/**
 * @typedef {Object} Worker
 * @property {string} id
 * @property {string} name
 * @property {string} platform
 * @property {string} location
 * @property {boolean} verified
 * @property {number} avgDailyEarnings
 * @property {string} joinDate
 */

/**
 * @typedef {Object} Payout
 * @property {string} id
 * @property {string} workerId
 * @property {string} claimId
 * @property {string} disruptionEvent
 * @property {number} amount
 * @property {'pending'|'approved'|'paid'|'rejected'} status
 * @property {string} date
 */

/**
 * @typedef {Object} Metrics
 * @property {number} totalWorkers
 * @property {number} activeCoverages
 * @property {number} pendingClaims
 * @property {number} payoutRate
 * @property {number} totalPayouts
 */
