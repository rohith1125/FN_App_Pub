from tensorflow import keras as ke
import tensorflow.python.keras.backend as K
from tensorflow.keras.models import Model, load_model
import streamlit as st
from nltk.tokenize import word_tokenize
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import re
import string
import nltk
import sklearn
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
import plotly.express as px
import plotly.graph_objects as go

MODEL_PATH = r"data/model/LSTM.h5"
MAX_NB_WORDS = 100000    # max no. of words for tokenizer
MAX_SEQUENCE_LENGTH = 200 # max length of each entry (sentence), including padding
VALIDATION_SPLIT = 0.2   # data for validation (not used in training)
EMBEDDING_DIM = 100
tokenizer_file = "tokenizer.pickle"

wordnet = WordNetLemmatizer()
regex = re.compile('[%s]' % re.escape(string.punctuation))

model_list = ["Logistic Regression",'Multinomial Naive Bayes Classifier','Bernoulli Naive Bayes Classifier','Gradient Boost Classifier','Decision Tree','RFC Classifier']
model_file_list = [r"data/model/LR_model.pkl",r"data/model/MNVBC_model.pkl",r"data/model/BNBC_model.pkl",r"data/model/GBC_model.pkl",r"data/model/DT_model.pkl",r"data/model/RFC_model.pkl"]

with open(tokenizer_file, 'rb') as handle:
    tokenizer = pickle.load(handle)

def basic_text_cleaning(line_from_column):
    # This function takes in a string, not a list or an array for the arg line_from_column

    tokenized_doc = word_tokenize(line_from_column)

    new_review = []
    for token in tokenized_doc:
        new_token = regex.sub(u'', token)
        if not new_token == u'':
            new_review.append(new_token)

    new_term_vector = []
    for word in new_review:
        if not word in stopwords.words('english'):
            new_term_vector.append(word)

    final_doc = []
    for word in new_term_vector:
        final_doc.append(wordnet.lemmatize(word))

    return ' '.join(final_doc)

@st.cache(allow_output_mutation=True)
def Load_model():
    model = load_model(MODEL_PATH)
    # model._make_predict_function()
    model.summary()  # included to make it visible when model is reloaded
    session = K.get_session()
    return model, session

if __name__ == '__main__':
    st.title('Fake News Classification')
    # st.write("Classifier using a LTSM model")
    # st.info("LSTM model, tokeniser and the 6 traditional machine learning models loaded ")
    st.subheader("Input the News content below")
    sentence = st.text_area("Enter your news content here", "Some news",height=200)
    predict_btt = st.button("predict")
    model, session = Load_model()
    if predict_btt:
        clean_text = []
        K.set_session(session)
        i = basic_text_cleaning(sentence)
        clean_text.append(i)
        sequences = tokenizer.texts_to_sequences(clean_text)
        data = pad_sequences(sequences, padding = 'post', maxlen = MAX_SEQUENCE_LENGTH)
        prediction = model.predict(data)

        # prediction_prob_real = prediction[0][0]
        # prediction_prob_fake = prediction[0][1]
        prediction_class = prediction.argmax(axis=-1)[0]

        st.header("Prediction using LSTM model")

        if (1-prediction) > 0.7:
            st.success('This is not fake news')
        elif prediction > 0.7:
            st.warning('This is a fake news')

        class_label = ["fake","true"]
        prob_list = [prediction*100,100-prediction*100]
        prob_dict = {"true/fake":class_label,"Probability":prob_list}
        df_prob = pd.DataFrame(prob_dict)
        fig = px.pie(df_prob, names='true/fake', values='Probability')
        model_option = "LSTM"
        if prediction > 0.7:
            fig.update_layout(title_text="{} model - prediction probability comparison between true and fake".format(model_option))
            st.info("The {} model predicts that there is a higher {} probability that the news content is fake compared to a {} probability of being true".format(model_option,prediction*100,(100-prediction*100)))
        elif (1-prediction) > 0.7:
            fig.update_layout(title_text="{} model - prediction probability comparison between true and fake".format(model_option))
            st.info("The {} model predicts that there is a higher {} probability that the news content is true compared to a {} probability of being fake".format(model_option,(100-prediction*100),prediction*100))
        else:
            fig.update_layout(title_text="{} model - prediction probability comparison between true and fake".format(model_option))
            st.info("Your news content is rather abstract, The {} model predicts that there a almost equal {} probability that the news content is true compared to a {} probability of being fake".format(model_option,(100-prediction*100),prediction*100))
        #st.plotly_chart(fig, use_container_width=True)
        # import matplotlib.pyplot as plt
        # plt.plot(prediction*100,100*(1-prediction))
        
        # plt.ylabel('LSTM model prediction probability')
        # plt.show()
        # import matplotlib.pyplot as plt
        # import numpy as np

        # fig, ax = plt.subplots()
        # ax.bar_chart(prob_list)

        # st.pyplot(fig)
        # chart_data = pd.DataFrame(
        # prob_list,
        # columns=["a", "b", "c"])

        # st.bar_chart(chart_data)
        import matplotlib.pyplot as plt
        li = [prediction[0]*100,100-prediction[0]*100]
        b = li[0]
        c = li[1]
        i = b[0]
        j = c[0]
        # st.info(i)
        # st.info(j)
        # st.info(li)
        # st.info(b)
        # print(len(li))
        # print(li.shape())
        k = [i,j]
        chart_data = pd.DataFrame(
        [i,j],
        columns=["news"])
 
        st.bar_chart(chart_data)
        
        # fig = px.pie(df_prediction, values='values', names='true/fake')
        # fig.update_layout(title_text="Comparision between all 7 models: Prediction proportion between True/Fake")
        #st.plotly_chart(fig, use_container_width=True)
        #st.table(df)


# Comparisons for other models
        # st.header("Prediction using 6 traditional machine learning model")
        # predictions = []
        # for model in model_file_list:
        #     filename = model
        #     model = pickle.load(open(filename, "rb"))
        #     prediction = model.predict([sentence])[0]
        #     predictions.append(prediction)

        # dict_prediction = {"Models":model_list,"predictions":predictions}
        # df = pd.DataFrame(dict_prediction)

        # num_values = df["predictions"].value_counts().tolist()
        # num_labels = df["predictions"].value_counts().keys().tolist()

        # dict_values = {"true/fake":num_labels,"values":num_values}
        # df_prediction = pd.DataFrame(dict_values)
        # fig = px.pie(df_prediction, values='values', names='true/fake')
        # fig.update_layout(title_text="Comparision between all 7 models: Prediction proportion between True/Fake")
        # st.plotly_chart(fig, use_container_width=True)
        # st.table(df)