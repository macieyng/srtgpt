class Subtitle:
    """
    This class takes four arguments in its constructor:

    index: The index of the subtitle.
    start_time: The start time of the subtitle in seconds.
    end_time: The end time of the subtitle in seconds.
    text: The text of the subtitle.
    It also has a __repr__ method to provide a string representation of the object, which will be useful for debugging. The __str__ method returns a string representation of the subtitle in the .srt format.

    You can create a Subtitle object like this:

    python
    Copy code
    subtitle = Subtitle(index=1, start_time=1.23, end_time=4.56, text="This is a subtitle.")
    print(subtitle)
    # Output:
    # 1
    # 1.23 --> 4.56
    # This is a subtitle.
    You can also access the attributes of the Subtitle object directly:

    python
    Copy code
    print(subtitle.index)     # Output: 1
    print(subtitle.start_time)  # Output: 1.23
    print(subtitle.end_time)   # Output: 4.56
    print(subtitle.text)     # Output: This is a subtitle.
    """
    def __init__(self, index, start_time, end_time, text):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text

    def __repr__(self):
        return f"<Subtitle {self.index}: {self.text[:20]}...>"

    def __str__(self):
        return f"{self.index}\n{self.start_time} --> {self.end_time}\n{self.text}\n"
    
    def replace_text(self, new_text):
        return Subtitle(self.index, self.start_time, self.end_time, new_text)
    
    def as_text(self):
        return str(self)


class SRTFile:
    """This SRTFile class has three methods:

    parse: This method parses the .srt file and stores the subtitles in a list of Subtitle objects.
    write: This method writes the list of Subtitle objects back to a .srt file.
    add_subtitle: This method adds a Subtitle object to the list of subtitles.
    You can create a SRTFile object like this:

    python
    Copy code
    srt_file = SRTFile("example.srt")
    srt_file.parse()
    You can add a Subtitle object to the SRTFile like this:

    python
    Copy code
    subtitle = Subtitle(index=1, start_time=1.23, end_time=4.56, text="This is a subtitle.")
    srt_file.add_subtitle(subtitle)
    You can write the list of Subtitle objects back to a .srt file like this:

    python
    Copy code
    srt_file.write("new_file.srt")
    Note that the write method will overwrite the existing file if it already exists. If you want to avoid overwriting the file, you can give a different file name.
    """
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.subtitles: list[Subtitle] = []

    def parse(self):
        with open(self.filepath, "r") as f:
            groups = []
            group = []
            for line in f.readlines():
                group.append(line)
                # print(f"Line: '{line}'")
                if line == "\n":
                    groups.append(group)
                    group = []
                    
        print(f"Subtitles discovered: {len(groups)}") 
        
        for group in groups:
            index = group[0].strip()
            start, end = group[1].strip().split(" --> ")
            
            self.subtitles.append(Subtitle(
                index=index,
                start_time=start,
                end_time=end,
                text="".join(group[2:])
            ))
                
        print(f"Subtitles parsed: {len(self.subtitles)}")

    def write(self):
        with open(self.filepath, "w") as f:
            for subtitle in self.subtitles:
                f.write(subtitle.as_text())

    def add_subtitle(self, subtitle):
        self.subtitles.append(subtitle)
