#!/usr/bin/env node

/**
 * SoloHeart UI - Setup Test Script
 * 
 * This script verifies that the development environment is properly configured.
 * Run this before starting the development server.
 */

const fs = require('fs');
const path = require('path');

console.log('🎲 SoloHeart UI - Setup Test\n');

// Check if we're in the right directory
const packageJsonPath = path.join(__dirname, 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('❌ Error: package.json not found. Make sure you\'re in the soloheart-ui directory.');
  process.exit(1);
}

// Check package.json
try {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  console.log('✅ package.json found');
  
  // Check required dependencies
  const requiredDeps = ['react', 'react-dom', 'react-markdown', 'axios', 'tailwindcss'];
  const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
  
  if (missingDeps.length > 0) {
    console.log(`⚠️  Missing dependencies: ${missingDeps.join(', ')}`);
    console.log('   Run: npm install');
  } else {
    console.log('✅ All required dependencies found');
  }
} catch (error) {
  console.error('❌ Error reading package.json:', error.message);
}

// Check environment file
const envPath = path.join(__dirname, '.env.development');
if (fs.existsSync(envPath)) {
  console.log('✅ .env.development found');
  
  const envContent = fs.readFileSync(envPath, 'utf8');
  if (envContent.includes('REACT_APP_MOCK_MODE=true')) {
    console.log('✅ Mock mode enabled');
  } else {
    console.log('⚠️  Mock mode not enabled');
  }
} else {
  console.log('⚠️  .env.development not found - creating default config');
  
  const defaultEnv = `# Development Environment Configuration
REACT_APP_MOCK_MODE=true
REACT_APP_API_URL=http://localhost:5001
REACT_APP_DEBUG=true
`;
  
  fs.writeFileSync(envPath, defaultEnv);
  console.log('✅ Created .env.development with default settings');
}

// Check source files
const srcPath = path.join(__dirname, 'src');
if (fs.existsSync(srcPath)) {
  console.log('✅ src directory found');
  
  const requiredFiles = [
    'App.tsx',
    'index.tsx',
    'index.css',
    'components/ChatWindow.tsx',
    'components/InputBox.tsx',
    'components/Sidebar.tsx',
    'utils/api.ts'
  ];
  
  const missingFiles = requiredFiles.filter(file => 
    !fs.existsSync(path.join(srcPath, file))
  );
  
  if (missingFiles.length > 0) {
    console.log(`❌ Missing source files: ${missingFiles.join(', ')}`);
  } else {
    console.log('✅ All source files found');
  }
} else {
  console.log('❌ src directory not found');
}

// Check configuration files
const configFiles = [
  'tailwind.config.js',
  'postcss.config.js',
  'tsconfig.json'
];

configFiles.forEach(file => {
  if (fs.existsSync(path.join(__dirname, file))) {
    console.log(`✅ ${file} found`);
  } else {
    console.log(`⚠️  ${file} not found`);
  }
});

console.log('\n📋 Setup Summary:');
console.log('================');

if (fs.existsSync(path.join(__dirname, 'node_modules'))) {
  console.log('✅ Dependencies installed');
  console.log('🚀 Ready to start development server:');
  console.log('   npm start');
} else {
  console.log('⚠️  Dependencies not installed');
  console.log('📦 Install dependencies:');
  console.log('   npm install');
}

console.log('\n🎮 Mock Mode Status:');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  if (envContent.includes('REACT_APP_MOCK_MODE=true')) {
    console.log('✅ Mock mode enabled - app will run offline');
    console.log('   To test with backend: set REACT_APP_MOCK_MODE=false');
  } else {
    console.log('⚠️  Mock mode disabled - backend required');
    console.log('   To enable mock mode: set REACT_APP_MOCK_MODE=true');
  }
}

console.log('\n🔧 Next Steps:');
console.log('1. Install dependencies: npm install');
console.log('2. Start development server: npm start');
console.log('3. Open http://localhost:3000');
console.log('4. Check browser console for detailed logs');
console.log('5. Test mock mode functionality');

console.log('\n✨ Happy coding!');
