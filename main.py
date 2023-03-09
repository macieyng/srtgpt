import argparse
import os
import re
import openai
import logging
from pathlib import Path
from srt import SRTFile, Subtitle
import random


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPEN_AI_API_KEY")

# Define the maximum number of characters that can be translated in a single API request
MAX_CHARS_PER_REQUEST = 2000

class Batcher:
    def __init__(self, subtitles: list[Subtitle], batch_size, delimiter="\n\n"):
        self.subtitles = subtitles
        self.batch_size = batch_size
        self.delimiter = delimiter

    def get_batches(self):
        batches = []
        text = "".join([s.as_text() for s in self.subtitles])
        while text:
            if len(text) > self.batch_size:
                chunk, text = text[:self.batch_size], text[self.batch_size:]
                last_delimiter_start = chunk.rfind(self.delimiter)
                chunk, text = chunk[:last_delimiter_start], chunk[last_delimiter_start:] + text
            else:
                chunk, text = text, ''
            batches.append(chunk)
            txt = chunk.replace('\n', '')
            print(f"Chunk: '{txt}'")
        return batches


def count_occurrences(string, substring):
    count = 0
    start_index = 0
    while True:
        index = string.find(substring, start_index)
        if index == -1:
            break
        count += 1
        start_index = index + len(substring)
    return count


def translate_text(text, target_language, batch_cnt, moderation=None) -> str:
    """Translate text into the specified target language using the OpenAI API."""
    if batch_cnt == 0 and not moderation:
        prompt = f"Here is a part of SRT file. Translate it into {target_language}. Keep the original formating of SRT file.\nRemember that I want you to translate the content to {target_language}.\n"
    else:
        if not moderation:
            prompt = random.choice(["You're doing a good job! ", "Good job! ", "Wonderful! ", "Great! ", "Nice! ", "Sounds good! "])
        else:
            prompt = moderation
        prompt += random.choice(["Keep the original SRT format. ", "Original text is in SRT format. Make output in SRT format too.", "Can you maintain SRT format? ", "Stick to the SRT format please. "])
        prompt += random.choice([f"Here is part of that text to translate to {target_language}. ", f"Here is some text to translate to {target_language}. ", f"Can you translate that for me to {target_language}? ", f"There is some transalation I need. Can you help me translating to {target_language}? "])
    prompt += "Text to translate is placed between symbols [[ and ]]"
    logger.info("Sending prompt: %s", prompt)
    prompt += f"\n[[\n{text}\n]]"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        n=1,
    )
    logger.info("%s", response)
    translation = response.choices[0].message.content.strip()
    return translation


def display_progress(current, total):
    percent = round(current * 100 / total)
    logger.info("Progress %s (%s of %s)", percent, current, total)


def translate_srt_file(input_file_path, output_directory, target_languages):
    """Translate the contents of an SRT file into the specified target languages."""
    input_file = Path(input_file_path)
    if not input_file.is_file() or not input_file.name.endswith('.srt'):
        print('Error: Invalid input file specified. Please provide a valid SRT file.')
        return
    
    srt_file = SRTFile(input_file)
    srt_file.parse()
    target_files = {lang: SRTFile(Path(input_file_path.replace(".srt", f"_{lang}.srt"))) for lang in target_languages}
    
    # Translate each subtitle into the specified target languages
    batches = Batcher(srt_file.subtitles, MAX_CHARS_PER_REQUEST).get_batches()
    total_subtitle = len(batches)
    translated_subtitles = []
    for target_lang in target_languages:
        target_file = target_files[target_lang]
        cancel_transalation = False
        for idx, batch in enumerate(batches):
            moderation = None
            if cancel_transalation:
                break
            while True:
                try:
                    display_progress(idx, total_subtitle)
                    # print(target_lang, batch)
                    print("$$$$$$$$$$$$$$$$$$$$")
                    translated = translate_text(batch, target_language=target_lang, batch_cnt=idx, moderation=moderation)
                    # print(translated)
                    print("########################")
                    for subtitle in translated.split("\n\n"):
                        subtitle = subtitle.strip()
                        parts = subtitle.split("\n")
                        print(parts)
                        if len(parts) < 3:
                            if parts == ["[["] or parts == ["]]"]:
                                logger.warning("Unparsable parts were found: %s", parts)
                                continue
                            raise ValueError("Not enough values to unpack.")
                        index, (start, end), text = parts[0], parts[1].split("-->"), parts[2:]
                        target_file.add_subtitle(
                            Subtitle(
                                index=index,
                                start_time=start,
                                end_time=end,
                                text="\n".join(text)
                            )
                        )
                except ValueError as exc:
                    logger.warning("%s: %s", type(exc), str(exc))
                    moderation = "The output is not what I asked you. Please stick to the original prompt. Focus on translating the content."
                except Exception:
                    cancel_transalation = True
                    break
                else:
                    break

        target_file.write()
        if len(target_file.subtitles) != len(srt_file.subtitles):
            logger.warning("Amount of subtitles doesn't match. Actual: %s, expected: %s", len(translated_subtitles), len(srt_file.subtitles))


if __name__ == '__main__':
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description='Translate an SRT file into one or more languages using the OpenAI API.')
    parser.add_argument('input_file', type=str, help='the path to the input SRT file')
    parser.add_argument('output_directory', type=str, help='the directory to output the translated SRT files')
    parser.add_argument('target_languages', nargs='+', type=str, help='the target languages to translate the input file into (specified as valid language codes)')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Translate the SRT file into the specified target languages
    logger.info("Arguemnts: input %s, output %s, lang %s", args.input_file, args.output_directory, args.target_languages)
    translate_srt_file(args.input_file, args.output_directory, args.target_languages)