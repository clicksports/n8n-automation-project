// Test script to verify frontend URL generation function
function generateFrontendUrl(productName, articleNumber, baseUrl = 'https://shop.held.de') {
  // Convert product name to URL-friendly format
  // Remove special characters, replace spaces with hyphens, handle German umlauts
  let urlName = productName
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss')
    .replace(/Ä/g, 'Ae')
    .replace(/Ö/g, 'Oe')
    .replace(/Ü/g, 'Ue')
    .replace(/[^a-zA-Z0-9\s-]/g, '') // Remove special characters except spaces and hyphens
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
    .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
  
  // Construct the URL following the pattern: baseUrl/Product-Name/article-number
  const frontendUrl = `${baseUrl}/${urlName}/${articleNumber}`;
  
  console.log(`🔗 Generated frontend URL: ${frontendUrl}`);
  return frontendUrl;
}

// Test cases
console.log('=== FRONTEND URL GENERATION TESTS ===');

// Test 1: Current product (Inuit Heizhandschuh)
const url1 = generateFrontendUrl('Inuit Heizhandschuh', '022572-00');
console.log(`Expected: https://shop.held.de/Inuit-Heizhandschuh/022572-00`);
console.log(`Generated: ${url1}`);
console.log(`✅ Match: ${url1 === 'https://shop.held.de/Inuit-Heizhandschuh/022572-00'}\n`);

// Test 2: Product with umlauts (like the example)
const url2 = generateFrontendUrl('Manzano Top Sportliche Tourenjacke', '062424-00-069-0-S');
console.log(`Expected: https://shop.held.de/Manzano-Top-Sportliche-Tourenjacke/062424-00-069-0-S`);
console.log(`Generated: ${url2}`);
console.log(`✅ Match: ${url2 === 'https://shop.held.de/Manzano-Top-Sportliche-Tourenjacke/062424-00-069-0-S'}\n`);

// Test 3: Product with German umlauts
const url3 = generateFrontendUrl('Kühl Handschuh für Winter', '123456-00');
console.log(`Expected: https://shop.held.de/Kuehl-Handschuh-fuer-Winter/123456-00`);
console.log(`Generated: ${url3}`);
console.log(`✅ Match: ${url3 === 'https://shop.held.de/Kuehl-Handschuh-fuer-Winter/123456-00'}\n`);

// Test 4: Product with special characters
const url4 = generateFrontendUrl('Test-Produkt (Special) & More!', '789012-00');
console.log(`Expected: https://shop.held.de/Test-Produkt-Special-More/789012-00`);
console.log(`Generated: ${url4}`);
console.log(`✅ Match: ${url4 === 'https://shop.held.de/Test-Produkt-Special-More/789012-00'}\n`);

console.log('=== TEST SUMMARY ===');
console.log('All URL generation tests completed!');