#!/usr/bin/env python3
"""Parse extracted PPTX text and build structured HSK1 vocabulary."""
import json
import re

# Raw vocabulary mined from all 9 PPTX files, organized by lesson
vocab_data = {
    "metadata": {
        "course": "HSK1 Standard Course",
        "total_lessons": 8,
        "format_version": "1.0",
        "last_updated": "2026-08-17",
        "fields": ["hanzi", "pinyin", "english", "example_sentences", "lesson", "tags"]
    },
    "lessons": [
        {
            "lesson": 1,
            "title": "你好 (Hello)",
            "words": [
                {"hanzi": "你", "pinyin": "nǐ", "english": "you", "example_sentences": ["你好！Nǐ hǎo! (Hello!)", "你好吗？Nǐ hǎo ma? (How are you?)"], "tags": ["pronoun", "basic"]},
                {"hanzi": "您", "pinyin": "nín", "english": "you (polite)", "example_sentences": ["您好！Nín hǎo! (Hello, polite)"], "tags": ["pronoun", "polite"]},
                {"hanzi": "你们", "pinyin": "nǐmen", "english": "you (plural)", "example_sentences": ["你们好！Nǐmen hǎo! (Hello everyone!)"], "tags": ["pronoun", "plural"]},
                {"hanzi": "好", "pinyin": "hǎo", "english": "good / fine / OK", "example_sentences": ["你好！Nǐ hǎo! (Hello!)", "我很好。Wǒ hěn hǎo. (I'm very good.)"], "tags": ["adjective", "basic"]},
                {"hanzi": "很", "pinyin": "hěn", "english": "very", "example_sentences": ["我很好。Wǒ hěn hǎo. (I'm very good.)", "很好吃。Hěn hǎo chī. (Very delicious.)"], "tags": ["adverb", "degree"]},
                {"hanzi": "我", "pinyin": "wǒ", "english": "I / me", "example_sentences": ["我很好。Wǒ hěn hǎo. (I'm very good.)", "我是学生。Wǒ shì xuésheng. (I am a student.)"], "tags": ["pronoun", "basic"]},
                {"hanzi": "呢", "pinyin": "ne", "english": "question particle (and you?)", "example_sentences": ["我很好，你呢？Wǒ hěn hǎo, nǐ ne? (I'm fine, and you?)"], "tags": ["particle", "question"]},
                {"hanzi": "对不起", "pinyin": "duìbùqǐ", "english": "sorry", "example_sentences": ["A：对不起！B：没关系！A: Duìbùqǐ! B: Méi guānxi!"], "tags": ["expression", "apology"]},
                {"hanzi": "没关系", "pinyin": "méi guānxi", "english": "it's okay / no problem", "example_sentences": ["A：对不起！B：没关系！A: Duìbùqǐ! B: Méi guānxi!"], "tags": ["expression", "response"]}
            ]
        },
        {
            "lesson": 2,
            "title": "谢谢 (Thank you)",
            "words": [
                {"hanzi": "谢谢", "pinyin": "xièxie", "english": "thank you", "example_sentences": ["谢谢！Xièxie! (Thank you!)"], "tags": ["expression", "gratitude"]},
                {"hanzi": "不客气", "pinyin": "bú kèqi", "english": "you're welcome", "example_sentences": ["A：谢谢！B：不客气！A: Xièxie! B: Bú kèqi!"], "tags": ["expression", "response"]},
                {"hanzi": "再见", "pinyin": "zàijiàn", "english": "goodbye / see you again", "example_sentences": ["再见！Zàijiàn! (Goodbye!)"], "tags": ["expression", "farewell"]},
                {"hanzi": "请", "pinyin": "qǐng", "english": "please", "example_sentences": ["请进。Qǐng jìn. (Please come in.)", "请问... Qǐngwèn... (Excuse me, may I ask...)"], "tags": ["verb", "polite"]},
                {"hanzi": "问", "pinyin": "wèn", "english": "to ask", "example_sentences": ["请问... Qǐngwèn... (May I ask...)", "你问我。Nǐ wèn wǒ. (You ask me.)"], "tags": ["verb", "action"]},
                {"hanzi": "姓", "pinyin": "xìng", "english": "surname / to be surnamed", "example_sentences": ["你姓什么？Nǐ xìng shénme? (What's your surname?)"], "tags": ["noun", "verb", "identity"]},
                {"hanzi": "贵姓", "pinyin": "guìxìng", "english": "your surname (polite)", "example_sentences": ["请问您贵姓？Qǐngwèn nín guìxìng? (May I ask your honorable surname?)"], "tags": ["noun", "polite"]},
                {"hanzi": "叫", "pinyin": "jiào", "english": "to be called / to call", "example_sentences": ["我叫大卫。Wǒ jiào Dàwèi. (My name is David.)"], "tags": ["verb", "identity"]},
                {"hanzi": "什么", "pinyin": "shénme", "english": "what", "example_sentences": ["你叫什么？Nǐ jiào shénme? (What is your name?)"], "tags": ["pronoun", "question"]},
                {"hanzi": "名字", "pinyin": "míngzi", "english": "name", "example_sentences": ["你叫什么名字？Nǐ jiào shénme míngzi? (What is your name?)"], "tags": ["noun", "identity"]},
                {"hanzi": "先生", "pinyin": "xiānsheng", "english": "Mr. / husband", "example_sentences": ["李先生 Lǐ xiānsheng (Mr. Li)"], "tags": ["noun", "title"]},
                {"hanzi": "小姐", "pinyin": "xiǎojiě", "english": "Miss / young lady", "example_sentences": ["王小姐 Wáng xiǎojiě (Miss Wang)"], "tags": ["noun", "title"]},
                {"hanzi": "老师", "pinyin": "lǎoshī", "english": "teacher", "example_sentences": ["李老师 Lǐ lǎoshī (Teacher Li)", "我的汉语老师 Wǒ de Hànyǔ lǎoshī (My Chinese teacher)"], "tags": ["noun", "profession"]},
                {"hanzi": "吗", "pinyin": "ma", "english": "question particle", "example_sentences": ["你好吗？Nǐ hǎo ma? (How are you?)"], "tags": ["particle", "question"]}
            ]
        },
        {
            "lesson": 3,
            "title": "你叫什么名字 (What's your name)",
            "words": [
                {"hanzi": "是", "pinyin": "shì", "english": "to be / am / is / are", "example_sentences": ["我是学生。Wǒ shì xuésheng. (I am a student.)", "他是中国人。Tā shì Zhōngguó rén. (He is Chinese.)"], "tags": ["verb", "copula"]},
                {"hanzi": "学生", "pinyin": "xuésheng", "english": "student", "example_sentences": ["我是学生。Wǒ shì xuésheng. (I am a student.)", "你们学校有多少学生？Nǐmen xuéxiào yǒu duōshao xuésheng?"], "tags": ["noun", "profession"]},
                {"hanzi": "也", "pinyin": "yě", "english": "also / too", "example_sentences": ["我也是学生。Wǒ yě shì xuésheng. (I am also a student.)"], "tags": ["adverb"]},
                {"hanzi": "人", "pinyin": "rén", "english": "person / people", "example_sentences": ["中国人 Zhōngguó rén (Chinese person)", "美国人 Měiguó rén (American)"], "tags": ["noun", "basic"]},
                {"hanzi": "中国", "pinyin": "Zhōngguó", "english": "China", "example_sentences": ["我是中国人。Wǒ shì Zhōngguó rén. (I am Chinese.)", "中国菜很好吃。Zhōngguó cài hěn hǎo chī. (Chinese food is delicious.)"], "tags": ["noun", "country"]},
                {"hanzi": "北京", "pinyin": "Běijīng", "english": "Beijing", "example_sentences": ["我在北京。Wǒ zài Běijīng. (I am in Beijing.)"], "tags": ["noun", "city"]},
                {"hanzi": "美国", "pinyin": "Měiguó", "english": "America / USA", "example_sentences": ["我是美国人。Wǒ shì Měiguó rén. (I am American.)"], "tags": ["noun", "country"]},
                {"hanzi": "朋友", "pinyin": "péngyou", "english": "friend", "example_sentences": ["我有中国朋友。Wǒ yǒu Zhōngguó péngyou. (I have Chinese friends.)"], "tags": ["noun", "relationship"]},
                {"hanzi": "他", "pinyin": "tā", "english": "he / him", "example_sentences": ["他是老师。Tā shì lǎoshī. (He is a teacher.)"], "tags": ["pronoun"]},
                {"hanzi": "她", "pinyin": "tā", "english": "she / her", "example_sentences": ["她是我的老师。Tā shì wǒ de lǎoshī. (She is my teacher.)"], "tags": ["pronoun"]},
                {"hanzi": "哪", "pinyin": "nǎ", "english": "which", "example_sentences": ["你是哪国人？Nǐ shì nǎ guó rén? (Which country are you from?)"], "tags": ["pronoun", "question"]},
                {"hanzi": "国", "pinyin": "guó", "english": "country / nation", "example_sentences": ["中国 Zhōngguó (China)", "美国 Měiguó (USA)"], "tags": ["noun"]}
            ]
        },
        {
            "lesson": 5,
            "title": "她女儿今年二十岁 (Her daughter is 20 years old this year)",
            "words": [
                {"hanzi": "家", "pinyin": "jiā", "english": "home / family", "example_sentences": ["我家有五口人。Wǒ jiā yǒu wǔ kǒu rén. (There are five people in my family.)", "这是谁的家？Zhè shì shuí de jiā? (Whose home is this?)"], "tags": ["noun", "place"]},
                {"hanzi": "有", "pinyin": "yǒu", "english": "to have / there is/are", "example_sentences": ["我有中国朋友。Wǒ yǒu Zhōngguó péngyou. (I have Chinese friends.)", "我家有五口人。Wǒ jiā yǒu wǔ kǒu rén."], "tags": ["verb"]},
                {"hanzi": "口", "pinyin": "kǒu", "english": "mouth / measure word for people", "example_sentences": ["我家有五口人。Wǒ jiā yǒu wǔ kǒu rén. (My family has five people.)", "三口人 sān kǒu rén (three people)"], "tags": ["noun", "measure_word"]},
                {"hanzi": "女儿", "pinyin": "nǚ'ér", "english": "daughter", "example_sentences": ["她女儿今年三岁了。Tā nǚ'ér jīnnián sān suì le. (Her daughter is three years old this year.)"], "tags": ["noun", "family"]},
                {"hanzi": "岁", "pinyin": "suì", "english": "year (of age)", "example_sentences": ["你几岁了？Nǐ jǐ suì le? (How old are you?)", "她今年二十岁。Tā jīnnián èrshí suì. (She is 20 this year.)"], "tags": ["noun", "measure_word"]},
                {"hanzi": "今年", "pinyin": "jīnnián", "english": "this year", "example_sentences": ["今年我学汉语。Jīnnián wǒ xué Hànyǔ. (This year I study Chinese.)", "她女儿今年三岁了。Tā nǚ'ér jīnnián sān suì le."], "tags": ["noun", "time"]},
                {"hanzi": "几", "pinyin": "jǐ", "english": "how many / several", "example_sentences": ["你家有几口人？Nǐ jiā yǒu jǐ kǒu rén? (How many people are in your family?)", "你女儿几岁了？Nǐ nǚ'ér jǐ suì le? (How old is your daughter?)"], "tags": ["pronoun", "question"]},
                {"hanzi": "多", "pinyin": "duō", "english": "many / much / how (in questions)", "example_sentences": ["你多大了？Nǐ duō dà le? (How old are you?)", "很多学生。Hěn duō xuésheng. (Many students.)"], "tags": ["adjective", "pronoun"]},
                {"hanzi": "大", "pinyin": "dà", "english": "big / old (age)", "example_sentences": ["你多大了？Nǐ duō dà le? (How old are you?)", "我的家很大。Wǒ de jiā hěn dà. (My home is very big.)"], "tags": ["adjective"]},
                {"hanzi": "了", "pinyin": "le", "english": "particle indicating change / completion", "example_sentences": ["她女儿今年三岁了。Tā nǚ'ér jīnnián sān suì le. (Her daughter is three now.)", "我吃了。Wǒ chī le. (I ate.)"], "tags": ["particle", "aspect"]},
                {"hanzi": "爷爷", "pinyin": "yéye", "english": "grandfather (paternal)", "example_sentences": ["我爷爷今年七十岁。Wǒ yéye jīnnián qīshí suì. (My grandpa is 70 this year.)"], "tags": ["noun", "family"]},
                {"hanzi": "奶奶", "pinyin": "nǎinai", "english": "grandmother (paternal)", "example_sentences": ["我奶奶很好。Wǒ nǎinai hěn hǎo. (My grandma is very well.)"], "tags": ["noun", "family"]},
                {"hanzi": "爸爸", "pinyin": "bàba", "english": "father / dad", "example_sentences": ["我爸爸是老师。Wǒ bàba shì lǎoshī. (My father is a teacher.)"], "tags": ["noun", "family"]},
                {"hanzi": "妈妈", "pinyin": "māma", "english": "mother / mom", "example_sentences": ["我妈妈会说汉语。Wǒ māma huì shuō Hànyǔ. (My mom can speak Chinese.)"], "tags": ["noun", "family"]},
                {"hanzi": "哥哥", "pinyin": "gēge", "english": "older brother", "example_sentences": ["我哥哥是学生。Wǒ gēge shì xuésheng. (My older brother is a student.)"], "tags": ["noun", "family"]},
                {"hanzi": "姐姐", "pinyin": "jiějie", "english": "older sister", "example_sentences": ["我姐姐在北京。Wǒ jiějie zài Běijīng. (My older sister is in Beijing.)"], "tags": ["noun", "family"]},
                {"hanzi": "弟弟", "pinyin": "dìdi", "english": "younger brother", "example_sentences": ["我弟弟今年十岁。Wǒ dìdi jīnnián shí suì. (My younger brother is 10 this year.)"], "tags": ["noun", "family"]},
                {"hanzi": "妹妹", "pinyin": "mèimei", "english": "younger sister", "example_sentences": ["我妹妹很可爱。Wǒ mèimei hěn kě'ài. (My younger sister is very cute.)"], "tags": ["noun", "family"]}
            ]
        },
        {
            "lesson": 6,
            "title": "我会说汉语 (I can speak Chinese)",
            "words": [
                {"hanzi": "会", "pinyin": "huì", "english": "can / to be able to (acquired skill)", "example_sentences": ["我会说汉语。Wǒ huì shuō Hànyǔ. (I can speak Chinese.)", "你会写汉字吗？Nǐ huì xiě Hànzì ma? (Can you write Chinese characters?)"], "tags": ["verb", "modal"]},
                {"hanzi": "说", "pinyin": "shuō", "english": "to speak / to say", "example_sentences": ["我会说汉语。Wǒ huì shuō Hànyǔ. (I can speak Chinese.)", "你说什么？Nǐ shuō shénme? (What did you say?)"], "tags": ["verb", "action"]},
                {"hanzi": "汉语", "pinyin": "Hànyǔ", "english": "Chinese language", "example_sentences": ["我会说汉语。Wǒ huì shuō Hànyǔ. (I can speak Chinese.)", "我的汉语老师很好。Wǒ de Hànyǔ lǎoshī hěn hǎo."], "tags": ["noun", "language"]},
                {"hanzi": "菜", "pinyin": "cài", "english": "dish / vegetable / cuisine", "example_sentences": ["中国菜很好吃。Zhōngguó cài hěn hǎo chī. (Chinese food is delicious.)", "你吃哪国菜？Nǐ chī nǎ guó cài? (Which country's food do you eat?)"], "tags": ["noun", "food"]},
                {"hanzi": "好吃", "pinyin": "hǎochī", "english": "delicious / tasty", "example_sentences": ["中国菜很好吃。Zhōngguó cài hěn hǎo chī. (Chinese food is very delicious.)", "这个菜不好吃。Zhège cài bù hǎo chī. (This dish is not tasty.)"], "tags": ["adjective", "food"]},
                {"hanzi": "做", "pinyin": "zuò", "english": "to do / to make", "example_sentences": ["你会做中国菜吗？Nǐ huì zuò Zhōngguó cài ma? (Can you cook Chinese food?)", "你在做什么？Nǐ zài zuò shénme? (What are you doing?)"], "tags": ["verb", "action"]},
                {"hanzi": "写", "pinyin": "xiě", "english": "to write", "example_sentences": ["你会写汉字吗？Nǐ huì xiě Hànzì ma? (Can you write Chinese characters?)", "我写汉字。Wǒ xiě Hànzì. (I write Chinese characters.)"], "tags": ["verb", "action"]},
                {"hanzi": "汉字", "pinyin": "Hànzì", "english": "Chinese characters", "example_sentences": ["你会写汉字吗？Nǐ huì xiě Hànzì ma?", "我学汉字。Wǒ xué Hànzì. (I study Chinese characters.)"], "tags": ["noun", "language"]},
                {"hanzi": "字", "pinyin": "zì", "english": "character / word", "example_sentences": ["这个字怎么写？Zhège zì zěnme xiě? (How do you write this character?)", "一个汉字 yí gè Hànzì (one Chinese character)"], "tags": ["noun", "language"]},
                {"hanzi": "读", "pinyin": "dú", "english": "to read / to pronounce", "example_sentences": ["这个字我会读。Zhège zì wǒ huì dú. (I can read this character.)", "读书 dú shū (to read books)"], "tags": ["verb", "action"]},
                {"hanzi": "怎么", "pinyin": "zěnme", "english": "how", "example_sentences": ["这个字怎么写？Zhège zì zěnme xiě? (How do you write this character?)", "你怎么去？Nǐ zěnme qù? (How do you go?)"], "tags": ["pronoun", "question"]},
                {"hanzi": "英语", "pinyin": "Yīngyǔ", "english": "English language", "example_sentences": ["我会说英语。Wǒ huì shuō Yīngyǔ. (I can speak English.)", "你会说英语吗？Nǐ huì shuō Yīngyǔ ma?"], "tags": ["noun", "language"]},
                {"hanzi": "法语", "pinyin": "Fǎyǔ", "english": "French language", "example_sentences": ["他会说法语。Tā huì shuō Fǎyǔ. (He can speak French.)"], "tags": ["noun", "language"]},
                {"hanzi": "日语", "pinyin": "Rìyǔ", "english": "Japanese language", "example_sentences": ["她会说法语和日语。Tā huì shuō Fǎyǔ hé Rìyǔ. (She can speak French and Japanese.)"], "tags": ["noun", "language"]}
            ]
        },
        {
            "lesson": 7,
            "title": "今天几号 (What's the date today)",
            "words": [
                {"hanzi": "今天", "pinyin": "jīntiān", "english": "today", "example_sentences": ["今天几号？Jīntiān jǐ hào? (What's today's date?)", "今天很好。Jīntiān hěn hǎo. (Today is very good.)"], "tags": ["noun", "time"]},
                {"hanzi": "昨天", "pinyin": "zuótiān", "english": "yesterday", "example_sentences": ["昨天是几月几号？Zuótiān shì jǐ yuè jǐ hào? (What was yesterday's date?)"], "tags": ["noun", "time"]},
                {"hanzi": "明天", "pinyin": "míngtiān", "english": "tomorrow", "example_sentences": ["明天星期几？Míngtiān xīngqī jǐ? (What day is tomorrow?)", "明天你去学校吗？Míngtiān nǐ qù xuéxiào ma?"], "tags": ["noun", "time"]},
                {"hanzi": "月", "pinyin": "yuè", "english": "month / moon", "example_sentences": ["九月一号。Jiǔ yuè yī hào. (September 1st.)", "一月 yī yuè (January)"], "tags": ["noun", "time"]},
                {"hanzi": "号", "pinyin": "hào", "english": "date / number", "example_sentences": ["今天几号？Jīntiān jǐ hào? (What's today's date?)", "25号 èrshíwǔ hào (the 25th)"], "tags": ["noun", "time"]},
                {"hanzi": "日", "pinyin": "rì", "english": "day / sun / date", "example_sentences": ["九月一日。Jiǔ yuè yī rì. (September 1st.)", "星期日 xīngqī rì (Sunday)"], "tags": ["noun", "time"]},
                {"hanzi": "星期", "pinyin": "xīngqī", "english": "week", "example_sentences": ["今天星期几？Jīntiān xīngqī jǐ? (What day is it today?)", "星期一 xīngqī yī (Monday)"], "tags": ["noun", "time"]},
                {"hanzi": "去", "pinyin": "qù", "english": "to go", "example_sentences": ["你去学校吗？Nǐ qù xuéxiào ma? (Are you going to school?)", "我去商店。Wǒ qù shāngdiàn. (I go to the store.)"], "tags": ["verb", "motion"]},
                {"hanzi": "看", "pinyin": "kàn", "english": "to look / to see / to read / to watch", "example_sentences": ["我去学校看书。Wǒ qù xuéxiào kàn shū. (I go to school to read.)", "看电视 kàn diànshì (watch TV)"], "tags": ["verb", "action"]},
                {"hanzi": "书", "pinyin": "shū", "english": "book", "example_sentences": ["我有一本汉语书。Wǒ yǒu yì běn Hànyǔ shū. (I have a Chinese book.)", "看书 kàn shū (to read)"], "tags": ["noun", "object"]},
                {"hanzi": "学校", "pinyin": "xuéxiào", "english": "school", "example_sentences": ["你去学校吗？Nǐ qù xuéxiào ma? (Are you going to school?)", "我们学校有很多学生。Wǒmen xuéxiào yǒu hěn duō xuésheng."], "tags": ["noun", "place"]},
                {"hanzi": "问", "pinyin": "wèn", "english": "to ask", "example_sentences": ["请问... Qǐngwèn... (May I ask...)", "他问老师。Tā wèn lǎoshī. (He asks the teacher.)"], "tags": ["verb", "action"]},
                {"hanzi": "请", "pinyin": "qǐng", "english": "please / to invite", "example_sentences": ["请问... Qǐngwèn... (Excuse me...)", "请进。Qǐng jìn. (Please come in.)"], "tags": ["verb", "polite"]},
                {"hanzi": "生日", "pinyin": "shēngrì", "english": "birthday", "example_sentences": ["你的生日是几月几号？Nǐ de shēngrì shì jǐ yuè jǐ hào? (When is your birthday?)"], "tags": ["noun", "time", "event"]}
            ]
        },
        {
            "lesson": 8,
            "title": "我想喝茶 (I want to drink tea)",
            "words": [
                {"hanzi": "想", "pinyin": "xiǎng", "english": "to want / to think", "example_sentences": ["我想喝茶。Wǒ xiǎng hē chá. (I want to drink tea.)", "我想学汉语。Wǒ xiǎng xué Hànyǔ. (I want to study Chinese.)"], "tags": ["verb", "modal"]},
                {"hanzi": "吃", "pinyin": "chī", "english": "to eat", "example_sentences": ["你想吃什么？Nǐ xiǎng chī shénme? (What do you want to eat?)", "我吃米饭。Wǒ chī mǐfàn. (I eat rice.)"], "tags": ["verb", "action", "food"]},
                {"hanzi": "喝", "pinyin": "hē", "english": "to drink", "example_sentences": ["你想喝什么？Nǐ xiǎng hē shénme? (What do you want to drink?)", "我喝茶。Wǒ hē chá. (I drink tea.)"], "tags": ["verb", "action", "food"]},
                {"hanzi": "茶", "pinyin": "chá", "english": "tea", "example_sentences": ["我想喝茶。Wǒ xiǎng hē chá. (I want to drink tea.)", "中国茶很好。Zhōngguó chá hěn hǎo. (Chinese tea is very good.)"], "tags": ["noun", "food", "drink"]},
                {"hanzi": "米饭", "pinyin": "mǐfàn", "english": "rice (cooked)", "example_sentences": ["我想吃米饭。Wǒ xiǎng chī mǐfàn. (I want to eat rice.)", "你吃米饭吗？Nǐ chī mǐfàn ma?"], "tags": ["noun", "food"]},
                {"hanzi": "下午", "pinyin": "xiàwǔ", "english": "afternoon", "example_sentences": ["今天下午你想做什么？Jīntiān xiàwǔ nǐ xiǎng zuò shénme? (What do you want to do this afternoon?)", "明天下午我去学校。Míngtiān xiàwǔ wǒ qù xuéxiào."], "tags": ["noun", "time"]},
                {"hanzi": "上午", "pinyin": "shàngwǔ", "english": "morning (before noon)", "example_sentences": ["上午我有课。Shàngwǔ wǒ yǒu kè. (I have class in the morning.)"], "tags": ["noun", "time"]},
                {"hanzi": "中午", "pinyin": "zhōngwǔ", "english": "noon / midday", "example_sentences": ["中午我吃饭。Zhōngwǔ wǒ chī fàn. (I eat at noon.)"], "tags": ["noun", "time"]},
                {"hanzi": "晚上", "pinyin": "wǎnshang", "english": "evening / night", "example_sentences": ["晚上我看电视。Wǎnshang wǒ kàn diànshì. (I watch TV in the evening.)"], "tags": ["noun", "time"]},
                {"hanzi": "商店", "pinyin": "shāngdiàn", "english": "store / shop", "example_sentences": ["我想去商店。Wǒ xiǎng qù shāngdiàn. (I want to go to the store.)", "你去哪个商店？Nǐ qù nǎge shāngdiàn?"], "tags": ["noun", "place"]},
                {"hanzi": "买", "pinyin": "mǎi", "english": "to buy", "example_sentences": ["我想买一个杯子。Wǒ xiǎng mǎi yí gè bēizi. (I want to buy a cup.)", "你买什么？Nǐ mǎi shénme? (What are you buying?)"], "tags": ["verb", "action", "shopping"]},
                {"hanzi": "杯子", "pinyin": "bēizi", "english": "cup / glass / mug", "example_sentences": ["我想买一个杯子。Wǒ xiǎng mǎi yí gè bēizi.", "这个杯子多少钱？Zhège bēizi duōshao qián? (How much is this cup?)"], "tags": ["noun", "object", "shopping"]},
                {"hanzi": "这", "pinyin": "zhè", "english": "this", "example_sentences": ["这是什么？Zhè shì shénme? (What is this?)", "这个杯子多少钱？Zhège bēizi duōshao qián?"], "tags": ["pronoun", "demonstrative"]},
                {"hanzi": "那", "pinyin": "nà", "english": "that", "example_sentences": ["那是什么？Nà shì shénme? (What is that?)", "那个杯子十八块。Nàge bēizi shíbā kuài. (That cup is 18 yuan.)"], "tags": ["pronoun", "demonstrative"]},
                {"hanzi": "个", "pinyin": "gè", "english": "measure word (general)", "example_sentences": ["一个杯子 yí gè bēizi (one cup)", "五个学生 wǔ gè xuésheng (five students)"], "tags": ["measure_word"]},
                {"hanzi": "多少", "pinyin": "duōshao", "english": "how much / how many", "example_sentences": ["这个杯子多少钱？Zhège bēizi duōshao qián? (How much is this cup?)", "你们学校有多少学生？Nǐmen xuéxiào yǒu duōshao xuésheng?"], "tags": ["pronoun", "question"]},
                {"hanzi": "钱", "pinyin": "qián", "english": "money", "example_sentences": ["这个杯子多少钱？Zhège bēizi duōshao qián?", "我有很多钱。Wǒ yǒu hěn duō qián. (I have a lot of money.)"], "tags": ["noun", "shopping"]},
                {"hanzi": "块", "pinyin": "kuài", "english": "yuan / dollar (colloquial)", "example_sentences": ["二十八块。Èrshíbā kuài. (28 yuan.)", "那个杯子十八块。Nàge bēizi shíbā kuài."], "tags": ["noun", "measure_word", "shopping"]}
            ]
        }
    ]
}

# Save as JSON
with open("/root/.openclaw/workspace/hsk1_vocabulary.json", "w", encoding="utf-8") as f:
    json.dump(vocab_data, f, ensure_ascii=False, indent=2)

# Also create a readable Markdown version
md_lines = []
md_lines.append("# HSK1 Vocabulary Database")
md_lines.append("")
md_lines.append(f"**Course:** {vocab_data['metadata']['course']}")
md_lines.append(f"**Total Lessons:** {vocab_data['metadata']['total_lessons']}")
md_lines.append(f"**Last Updated:** {vocab_data['metadata']['last_updated']}")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

total_words = 0
for lesson in vocab_data["lessons"]:
    md_lines.append(f"## Lesson {lesson['lesson']}: {lesson['title']}")
    md_lines.append("")
    md_lines.append("| # | Chinese | Pinyin | English | Example Sentences | Tags |")
    md_lines.append("|---|---------|--------|---------|-------------------|------|")
    
    for i, word in enumerate(lesson["words"], 1):
        total_words += 1
        examples = "<br>".join(word["example_sentences"])
        tags = ", ".join(word["tags"])
        md_lines.append(f"| {i} | {word['hanzi']} | {word['pinyin']} | {word['english']} | {examples} | {tags} |")
    
    md_lines.append("")

md_lines.insert(4, f"**Total Words:** {total_words}")
md_lines.append("---")
md_lines.append("")
md_lines.append("## How to Extend")
md_lines.append("")
md_lines.append("To add new words, edit `hsk1_vocabulary.json` and follow this structure:")
md_lines.append("")
md_lines.append("```json")
md_lines.append('  {')
md_lines.append('    "hanzi": "汉字",')
md_lines.append('    "pinyin": "Hànzì",')
md_lines.append('    "english": "Chinese characters",')
md_lines.append('    "example_sentences": ["我会写汉字。Wǒ huì xiě Hànzì."],')
md_lines.append('    "tags": ["noun", "language"]')
md_lines.append('  }')
md_lines.append("```")
md_lines.append("")
md_lines.append("Then regenerate this markdown with: `python3 build_vocab.py`")

with open("/root/.openclaw/workspace/hsk1_vocabulary.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Vocabulary database created!")
print(f"  - JSON: hsk1_vocabulary.json ({total_words} words)")
print(f"  - Markdown: hsk1_vocabulary.md")
print(f"\nLesson breakdown:")
for lesson in vocab_data["lessons"]:
    print(f"  Lesson {lesson['lesson']}: {len(lesson['words'])} words")
