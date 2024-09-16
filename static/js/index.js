async function fetchSolanaData() {
    const response = await fetch('https://api.solana.com/blockchain-data'); // Example URL
    const data = await response.json();

    // Update the UI with the fetched data
    document.getElementById('block-number').innerText = data.blockNumber;
    document.getElementById('transaction-count').innerText = data.transactionCount;
    document.getElementById('time').innerText = data.time;
}

fetchSolanaData();
