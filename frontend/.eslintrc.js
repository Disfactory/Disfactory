module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/essential',
    '@vue/standard',
    '@vue/typescript/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    quotes: 'off',
    '@typescript-eslint/quotes': ['error', 'single'],
    '@typescript-eslint/explicit-function-return-type': 'off',
    'semi': 'off',
    '@typescript-eslint/semi': ['error', 'never'],
    'no-unused-expressions': 'off',
    '@typescript-eslint/no-unused-expressions': 'error',
    '@typescript-eslint/member-delimiter-style': ['error', { multiline: { delimiter: 'comma', requireLast: false }, singleline: { delimiter: 'comma', requireLast: false }, overrides: { interface: { multiline: { delimiter: 'none' } } } }],
    '@typescript-eslint/require-await': 'off', // TODO: can remove on 11/25
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    project: 'tsconfig.json',
    sourceType: 'module',
    extraFileExtensions: ['.vue']
  },
  overrides: [
    {
      files: [
        '**/__tests__/*.{j,t}s?(x)',
        '**/tests/unit/**/*.spec.{j,t}s?(x)'
      ],
      env: {
        mocha: true
      }
    }
  ]
}
