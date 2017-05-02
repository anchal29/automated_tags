# Automated tag generation for stack overflow questions

Under this project we tried to implement a system which could automatically assign tags to a stack overflow questions using Machine Learning algorithms.
Here we implemented three feature extraction techniques:
1. The most generic feature extraction consists of getting bags of words, then doing tf-idf of it to reweight the samples. Finally training a classifier(SVM and Multinomial Naive Bayes)  on it.
2. Using NLTK to preprocess the data followed by vectorizer of Scikit-Learn. Here SGDClassifier was used.
3. A 4-dimensional feature space consisting of:
    1. **Exact Title:** The tag is one of the words in the title. This has count of tags as output.
    2. **Exact Body:** The tag is one of the words in the body. This has count of tags as output.
    3. **Relaxed Title and Relaxed Body:** Are all tokens that are obtained by splitting tags at hyphens or any other special attribute contained in the title and body respectively.  This has minimum of count of each token of tags as output.

## Dependencies

1. Natural Language Toolkit along with the complete NLTK corpus, and
2. Sckit-Learn.

  #### Steps to install these dependencies:

    pip install nltk scikit-learn
    python -m nltk.downloader all

## Code Execution
    
Execute the bash script present in the root directory.

