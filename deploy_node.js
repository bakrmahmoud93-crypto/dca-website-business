const surge = require('surge');
const path = require('path');

const deployDir = path.join(__dirname, 'generated_sites', 'deploy_temp');
const domain = 'dca-dental-clinic.surge.sh';

console.log('Publishing to Surge...');

const surgeInstance = surge();

// Login first
surgeInstance.login({
  email: 'clawadam828@gmail.com',
  password: 'P@ssw0rd@123.com.'
}, (err, loggedIn) => {
  if (err) {
    console.error('Login error:', err);
    return;
  }
  
  console.log('Logged in! Deploying...');
  
  // Deploy
  surgeInstance.publish({
    project: deployDir,
    domain: domain
  }, (err, result) => {
    if (err) {
      console.error('Deploy error:', err);
    } else {
      console.log('Published to:', `https://${domain}`);
    }
  });
});
