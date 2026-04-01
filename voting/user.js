document.addEventListener('DOMContentLoaded', function() {
    // Sample candidate data (replace with actual data retrieval logic)
    const candidates = [
        { id: 1, name: 'Candidate A', age: 35, party: 'Party X' },
        { id: 2, name: 'Candidate B', age: 42, party: 'Party Y' },
        { id: 3, name: 'Candidate C', age: 38, party: 'Party Z'  }
    ];
    const candidatesList = document.getElementById('candidates-list');
    candidates.forEach(candidate => {
        const candidateDiv = document.createElement('div');
        candidateDiv.innerHTML = `
            <h3>${candidate.name}</h3>
            <p>Age: ${candidate.age}</p>
            <p>Party: ${candidate.party}</p>
        `;
        candidatesList.appendChild(candidateDiv);
    });
    const votingForm = document.getElementById('voting-form');
    votingForm.style.display = 'block';
    const candidateOptions = document.getElementById('candidate-options');
    candidates.forEach(candidate => {
        const option = document.createElement('input');
        option.type = 'radio';
        option.id = `vote-${candidate.id}`;
        option.name = 'vote';
        option.value = candidate.id;
        const label = document.createElement('label');
        label.htmlFor = `vote-${candidate.id}`;
        label.textContent = candidate.name;
        candidateOptions.appendChild(option);
        candidateOptions.appendChild(label);
        candidateOptions.appendChild(document.createElement('br'));
    });

    // Vote form submission
    const voteForm = document.getElementById('vote-form');
    voteForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const selectedCandidateId = document.querySelector('input[name="vote"]:checked');
        if (selectedCandidateId) {
            alert(`You voted for candidate ID: ${selectedCandidateId.value}`);
            window.location.href= 'vote.html';
        } else {
            alert('Please select a candidate to vote');
        }
    });
});
