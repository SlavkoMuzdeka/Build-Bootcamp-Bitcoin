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

Feel free to experiment, learn, and make modifications to the code as part of your learning journey. Remember that PNGCoin is a basic example designed for educational purposes, and its practical use is limited.

While I am learning from this boot camp experience and not actively contributing to the code, PNGCoin serves as an important starting point for my education within the "Build-Bootcamp" section. By examining and understanding these problems, I can gain valuable insights into the challenges of digital cash systems, which will inform my learning journey as I progress through this Build-Bootcamp-DigitalCash experience.
