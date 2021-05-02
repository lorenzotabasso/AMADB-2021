package process;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class PostProcessLexicalResource {

    private HashMap<Integer, String> emoSN = new HashMap<>();

    public void read(String path) {
        try {
            InputStream is = new FileInputStream(path);
            BufferedReader br = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));

            String line = br.readLine();
            for (int i = 0; line != null; i++) {
                emoSN.put(i, line);
                line = br.readLine();
            }
        } catch (IOException e) {
            System.out.println(e.getMessage());
        }
    }

    public void removeCompoundWords() {
        HashMap<Integer,String> deleted = new HashMap<>();
        int emoSizeInitial = emoSN.size();
        emoSN.entrySet().removeIf(
                entry -> {
                    if (entry.getValue().contains("_")) {
                        deleted.put(entry.getKey(), entry.getValue());
                        return true;
                    } else {
                        return false;
                    }
                });
        System.out.println("Deleted " + deleted.size() + " words.");
        System.out.println(emoSN);
        System.out.println("Remaining " + (emoSizeInitial - deleted.size()) + " words.");
    }

    public static void main(String[] args) {
        final String path = "/Users/lorenzotabasso/Desktop/Github/MAADB/Advanced_Database/data/lexical-resources/Anger/EmoSN_anger.txt";

        PostProcessLexicalResource pplr = new PostProcessLexicalResource();

        pplr.read(path);
        pplr.removeCompoundWords();
    }

}
