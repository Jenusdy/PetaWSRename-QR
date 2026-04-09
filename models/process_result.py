from dataclasses import dataclass


@dataclass
class ProcessResult:
    file_name: str
    output_name: str
    status: str
    info: str

    def to_list(self):
        return [self.file_name, self.output_name, self.status, self.info]