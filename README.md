# Build-Bootcamp-Bitcoin

Welcome to the Build-Bootcamp-DigitalCash project, where we explore and refine the concept of digital cash through the lens of a learning experience within the "Build-Bootcamp" section. In this boot camp, I am a participant focused on gaining valuable insights into digital currencies, guided by a curriculum that includes the examination of a series of coins, each with its unique characteristics and challenges. Throughout this educational journey, my aim is to gain a deeper understanding of digital cash systems, their complexities, and the iterative process of improving them.

## Introduction

In this project, we recognize that the path to innovation often begins with seemingly rudimentary ideas. The first coin we are introducing, known as PNGCoin, is intentionally designed with various shortcomings to emphasize the challenges inherent in early digital cash concepts. While I am in the process of learning and growing within the "Build-Bootcamp" section, it's important to note that PNGCoin, while far from practical for real-world use, provides a valuable starting point for my educational journey.

## PNGCoin

PNGCoin is our first exposure to digital cash, and it serves as a foundation for understanding subsequent coins in this project. In this initial iteration, I explore the basic design principles, even if they result in numerous challenges. Here's a brief overview of PNGCoin's characteristics and issues:

### Key Features:

- **Bearer Instrument:** PNGCoin operates on the principle of a bearer instrument, meaning that ownership of a coin is determined by possession of a list of .png photographs containing physical signatures. These photographs represent the transfer of ownership between parties. In essence, whoever holds the images owns the coin.

### Challenges and Limitations:

- **Easily Counterfeit:** PNGCoin is susceptible to counterfeiting due to the simplicity of replicating image files. This poses a significant security risk.

- **Easy to Forge:** Since the coin relies on physical signatures in image format, forging these signatures is relatively straightforward.

- **Prone to Double Spending:** The lack of a robust transaction validation mechanism makes PNGCoin vulnerable to double-spending, where the same coin can be used in multiple transactions.

- **Privacy and Fungibility Concerns:** PNGCoin exhibits poor privacy and fungibility characteristics. Fungibility refers to the idea that each coin should be indistinguishable from another, but with PNGCoin, each coin is uniquely represented by its set of images.

- **Zero Divisibility:** PNGCoin lacks divisibility, meaning that users cannot make fractional payments or transactions, which is a significant drawback in practical use.

- **Centralized Issuance:** PNGCoin is issued by a central authority, making it susceptible to censorship and control by a single entity.

### Running PNGCoin

If you'd like to explore PNGCoin, here are the steps to set up your environment and run the Jupyter notebook:

1. **Create a Virtual Environment:**

```bash
    # Creating a virtual environment

    # Unix/maxOS
    python3 -m venv env

    # Windows
    python -m venv env

    # Activating a virtual environment

    # Unix/maxOS
    source env/bin/activate

    # Windows
    .\env\Scripts\activate
```

2. **Install Dependencies:** With the virtual environment activated, install the required dependencies from the `requirements.txt` file:

```bash
    pip install -r requirements.txt
```

3. **Launch Jupyter Notebook:** Start the Jupyter notebook by running the following command:

```bash
    jupyter notebook
```

This will open a web browser with the Jupyter notebook interface.

4. **Open PNGCoin Notebook:** Within the Jupyter interface, navigate to the `PNGCoin.ipynb` notebook and open it. You can now explore and run the code related to PNGCoin.

## ECDSACoin

ECDSACoin is the second iteration of our digital cash project and shares many similarities with PNGCoin. However, there is a key difference: instead of relying on .png photographs of physical signatures for transaction verification, we implement ECDSA (Elliptic Curve Digital Signature Algorithm) digital signatures.

### Key Features:

- **Bearer Instrument:** Like PNGCoin, ECDSACoin operates on the principle of a bearer instrument. Ownership of a coin is determined by possession of the digital signature associated with that coin. In essence, whoever possesses the valid ECDSA signature has ownership of the coin.

### Improvements over PNGCoin:

- **Enhanced Security:** By replacing physical signatures with ECDSA digital signatures, ECDSACoin significantly improves security. ECDSA signatures are cryptographically secure and challenging to forge, making the coin resistant to counterfeiting and fraudulent transactions.

- **Reduced Risk of Double Spending:** ECDSACoin incorporates robust transaction validation mechanisms through digital signatures. This significantly reduces the risk of double-spending, ensuring that each coin can only be used once in a transaction.

- **Improved Privacy and Fungibility:** ECDSACoin enhances privacy and fungibility compared to PNGCoin. Each coin is no longer uniquely represented by physical images, enhancing the coin's indistinguishability from others, a crucial aspect of fungibility.

- **Partial Divisibility:** While ECDSACoin maintains some level of divisibility, it's not as limited as PNGCoin. Users can make fractional payments and transactions, increasing the coin's practicality for everyday use.

### Remaining Challenge: Double Spending

One of the primary challenges that remain with ECDSACoin is addressing the issue of double spending. While our transition to ECDSA digital signatures has significantly reduced the risk of double spending compared to PNGCoin, it is not entirely eliminated.

### Running ECDSACoin

The same as for PNGCoin.

## BankCoin

BankCoin is the third iteration of our digital cash project, and it is designed to address the double spend problem effectively. However, it comes with certain characteristics that set it apart from the previous coins.

### Key Features:

- **Double Spend Prevention:** BankCoin successfully solves the double spend problem, making it a more secure digital cash solution compared to its predecessors.

### Characteristics:

- **Transaction Construction Rigidity:** One notable characteristic of BankCoin is that it lacks flexibility in transaction construction. Unlike some other digital currencies, you cannot create complex transactions by combining multiple coins or paying multiple parties in a single transaction.

- **Single Coin Transactions:** With BankCoin, each transaction typically involves a single coin. You cannot spend multiple coins in a single transaction, which simplifies the transaction process but limits flexibility.

- **Labor-Intensive Transactions:** Paying with BankCoin can be labor-intensive compared to other digital currencies. The lack of flexibility in transaction construction means that users may need to perform multiple individual transactions for complex payment scenarios.

### Running BankCoin

To test and run BankCoin, you will need to set up a virtual environment and use pytest to run the provided test suite. Here are the steps:

1. **Create a Virtual Environment:** The same as for PNGCoin

2. **Install Dependencies:** The same as for PNGCoin

3. **Run Tests with `pytest`:** Use pytest to run the test suite. Assuming you have a bankcoin.py file and a bankcoin_tests.py file containing your tests, you can run the tests by executing the following command:

```bash
    pytest bankcoin_tests.py
```

This will run the tests and provide you with feedback on the functionality of BankCoin.

## BlockCoin

BlockCoin is the fourth iteration of our digital cash project, introduced in response to the issues identified with BankCoin. While BankCoin successfully prevented double spending, it introduced a centralization concern due to its monopoly structure. BlockCoin aims to address this concern by moving from a single "bank" to a system of multiple "banks," thus spreading power more evenly. However, it also introduces new challenges.

### Purpose and Characteristics:

- **Decentralization:** The main focus of BlockCoin is to move from a single "bank" to multiple "banks" that agree on validation rules. Each bank is assigned a numerical ID. These banks take turns nominating sets of transactions at regular intervals, creating what is commonly referred to as a "block." The non-nominating banks in each round verify the block submitted by the nominating bank. This decentralized approach aims to reduce the centralization of power seen in BankCoin.

- **Spreading Power:** By distributing the responsibility for transaction validation among multiple banks, BlockCoin aims to establish an oligopoly rather than a monopoly. This change in structure can help prevent the abuse of power and monopolistic control that may occur in a centralized system.

### Challenges and Considerations:

- **Censorship Risk:** While BlockCoin reduces the risk of central censorship, there is still a censorship risk. Certain transactions may remain unconfirmed if the banks collectively decide not to process them. The political nature of these banks may lead to behavior that maximizes their profit.

- **Dynamic Nomination:** BlockCoin's decentralized structure raises questions about how banks are assigned IDs and how new banks can join the system. A more open system where anyone can nominate blocks introduces the challenge of nominating new blocks in a dynamic and anarchic environment.

- **Introduction of Proof-of-Work:** To address the challenges of dynamic nomination in a free-for-all environment, BlockCoin introduces the concept of proof-of-work. This mechanism is commonly used in blockchain systems to provide security and facilitate block creation.

### Running BlockCoin

To run BlockCoin, you can follow the instructions provided in the documentation (likely using Docopt) associated with the codebase. The documentation should outline the steps for setting up and running the BlockCoin application.

## POWCoin

POWCoin, short for Proof of Work Coin, represents the fifth iteration of our digital cash project. This coin introduces the concept of a native internet protocol, addresses divisibility concerns, and seeks to solve the double-spending problem through a unique approach.

### Key Features:

- **Cryptographically Verifiable Transactions:** Similar to its predecessors, POWCoin features transactions that are cryptographically verifiable, ensuring security and integrity.

- **Enhanced Divisibility:** POWCoin has the potential for good divisibility, both in terms of inputs and outputs. Being software-based, it can be divided into smaller units, increasing flexibility in transactions.

- **Native Internet Protocol:** POWCoin operates on a native internet protocol, making transactions cheap and instant. This improvement enhances the efficiency and accessibility of transacting.

- **Double-Spend Prevention via a Political Cartel:** Unlike a single central bank, POWCoin introduces a political cartel to prevent double-spending issues. While there are more checks-and-balances in place compared to a single bank, it is still susceptible to potential corruption and centralization.

- **Resource-Driven Block Nomination:** To address centralization concerns, POWCoin introduces the concept of awarding block nomination privilege based on the consumption of a resource that cannot be easily monopolized. This approach aims to make the system censorship-resistant and Sybil-resistant.

- **Miner Subsidies:** To prevent Sybil attacks and to incentivize participation, POWCoin awards block nomination privilege based on cryptographically proven SHA256 hashrate expenditure. Miners are also rewarded with a fixed number of coins for every mining race, ensuring that mining costs are recouped.

- **Coinbase Transaction:** Miners add a special transaction known as the "coinbase transaction" when they construct a new block. This transaction pays the miner a preset number of coins and is handled separately in all transaction validation code.

- **Joining the Network:** POWCoin outlines the process of adding and connecting new nodes to the network, allowing for peer-to-peer interactions among participants.

- **Initial Block Download:** This section addresses how new participants can catch up with the network and download blocks efficiently. It describes a scheme for propagating blocks to new nodes.

- **Nakamoto Consensus:** POWCoin introduces Nakamoto Consensus, a mechanism for tracking branches or forks in the blockchain and making decisions on block extensions, creation of new branches, or block rejections.

### Running POWCoin

To run the POWCoin application, you can follow these steps:

1. Use the following command to build and start the POWCoin application using Docker Compose:

```bash
   docker-compose -f docker-compose-p2p.yml up --build
```

This command will initiate the POWCoin application using the specified Docker Compose configuration file. Please ensure that you have Docker and Docker Compose installed on your system before running this command.

To run the tests, use a testing framework like pytest or your preferred testing tool. If you're using pytest, you can run the tests by executing the following command in your terminal:

```bash
    pytest powcoin_tests.py
```

This will run the test suite defined in powcoin_tests.py and provide you with feedback on the functionality of your POWCoin project.
By running these tests, you can ensure that your POWCoin application functions as expected and verify its correctness.

Feel free to experiment, learn, and make modifications to the code as part of your learning journey. While I am learning from this boot camp experience and not actively contributing to the code. By examining and understanding these problems, I can gain valuable insights into the challenges of digital cash systems, which will inform my learning journey as I progress through this Build-Bootcamp-DigitalCash experience.
