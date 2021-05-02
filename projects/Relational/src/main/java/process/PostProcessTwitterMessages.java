package process;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.process.WordToSentenceProcessor;

import java.io.StringReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

public class PostProcessLexicalResource {

    private String sentence;
    private List<String> tokens;

    private final String[] punctuation = {",", ":", ";", "-", "_", "=", "^", "$", "%",
            "&", "/", "(", ")", "|", "£", "+", "<", ">", "#", "§", "[", "]", "{", "}",
            "°", "*", "."};

    public PostProcessLexicalResource() {
        this.sentence = null;
        this.tokens = null;
    }

    public PostProcessLexicalResource(String sentence, List<String> tokens) {
        this.sentence = sentence;
        this.tokens = tokens;
    }

    private void tokenize() {
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize,ssplit");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
        CoreDocument exampleDocument = new CoreDocument(sentence);
        pipeline.annotate(exampleDocument);
        List<CoreLabel> firstSentenceTokens = exampleDocument.sentences().get(0).tokens();
        for (CoreLabel token : firstSentenceTokens) {
            tokens.add(token.word());
        }
    }


    private void removePuntuation() {
        List<String> punt = Arrays.asList(punctuation);
        for (int i = 0; i < tokens.size(); i++) {
            if (punt.contains(tokens.get(i))) {
                tokens.remove(i);
            }
        }
    }

    public static List<String> tokenizeSentence(String text) {
        List<CoreLabel> tokens = new ArrayList<>();
        PTBTokenizer<CoreLabel> tokenizer = new PTBTokenizer<>(new StringReader(text), new CoreLabelTokenFactory(), "");
        while (tokenizer.hasNext()) {
            tokens.add(tokenizer.next());
        }

        List<List<CoreLabel>> sentences = new WordToSentenceProcessor<CoreLabel>().process(tokens);
        int end;
        int start = 0;
        List<String> sentenceList = new ArrayList<>();
        for (List<CoreLabel> sentence : sentences) {
            end = sentence.get(sentence.size() - 1).endPosition();
            sentenceList.add(text.substring(start, end).trim());
            start = end;
        }
        return sentenceList;
    }

}
