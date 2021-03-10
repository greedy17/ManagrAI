module.exports = {
  root: true,
  parserOptions: {
    parser: 'babel-eslint',
    sourceType: 'module'
  },
  // required to lint *.vue files
  plugins: [
    'html',
    'cypress'
  ],
  env: {
    mocha: true,
    'cypress/globals': true
  },
  extends: 'standard',
  // check if imports actually resolve
  settings: {
    'import/resolver': {
      webpack: {
        config: 'client/build/webpack.base.conf.js'
      }
    }
  },
  // add your custom rules here
  rules: {
    strict: 'off',
    // don't require .vue extension when importing
    'import/extensions': ['js', 'vue'],
    // disallow reassignment of function parameters
    // disallow parameter object manipulation except for specific exclusions
    'no-param-reassign': ['error', {
      props: true,
      ignorePropertyModificationsFor: [
        'state', // for vuex state
        'acc', // for reduce accumulators
        'e' // for e.returnvalue
      ]
    }],
    // allow comma dangle
    'comma-dangle': 0,
    // allow optionalDependencies
    'import/no-extraneous-dependencies': ['error', {
      optionalDependencies: ['test/unit/index.js']
    }],
    // allow debugger during development
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off'
  }
}
