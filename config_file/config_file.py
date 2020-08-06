from pathlib import Path
from shutil import copyfile
from typing import Any, Union

from config_file.config_file_path import ConfigFilePath
from config_file.exceptions import ParsingError
from config_file.parse_value import parse_value
from config_file.utils import Default


class ConfigFile:
    def __init__(self, file_path: Union[str, Path]) -> None:
        """
        Stores the config file path and expands it if needed, reads in
        the file contents, and determines what parser should be used for
        the given file.

        Args:
            file_path: The path to your configuration file.

        Raises:
            ValueError: If the specified file path does not have an extension
                        that is supported or it is a directory.
            FileNotFoundError: If the specified file path does not exist.
        """
        self.__path = ConfigFilePath(file_path).validate()
        self.__parser = self.__path.parser

    @property
    def file_path(self) -> Path:
        return Path(self.__path)

    @property
    def original_file_path(self) -> Path:
        return Path(self.__path.original_path)

    def __getitem__(self, key: str):
        return self.__parser.parsed_content[key]

    def __setitem__(self, key: str, value: Any):
        self.__parser.parsed_content[key] = value

    def __delitem__(self, key: str):
        del self.__parser.parsed_content[key]

    def get(
        self,
        key: str,
        parse_types: bool = False,
        return_type: Any = None,
        default: Any = Default(None),
    ) -> Any:
        """
        Retrieve the value of a key.

        Args:
            key: The key to retrieve.
            parse_types: Automatically parse ints, floats, booleans, dicts, and
                         lists. This recursively parses all types in whatever you're
                         retrieving, not just a single type.

                         e.g. If you are retrieving a section, all values in that
                         section will be parsed.

            return_type: The type to coerce the return value to.
            default: The default value to return if the value of the key is empty.

        Returns:
            The value of the key.

        Raises:
            ValueError: If the value is not able to be coerced into return_type.
        """
        try:
            key_value = self.__parser.get(key)
        except ParsingError as error:
            if default is not type(Default):
                key_value = default
            else:
                raise ParsingError(error)

        if parse_types:
            key_value = parse_value(key_value)

        return return_type(key_value) if return_type else key_value

    def set(self, key: str, value: Any) -> None:
        """Sets the value of a key.

        If the given key does not exist, it will be automatically
        created for you. That includes if there are multiple keys
        in a row that do not exist.
        e.g. set('exists.does_not.does_not.also_does_not', 5)

        The behavior of how this is done, however, depends on the
        file used. For example, with INI, subsections are not supported.
        So it would create a key in the section `exists` called `does_not`
        and set it to the value {'does_not': {'also_does_not': 5}}.

        Args:
            key: The section, sub-section, or key to delete.
            value: The value to set the key to.
        """
        self.__parser.set(key, value)

    def delete(self, key: str) -> None:
        """Deletes a section or key.

        Args:
            key: The section, sub-section, or key to delete.

        Raises:
            MissingKeyError: If a key is attempted to be deleted that
            does not exist.
        """
        self.__parser.delete(key)

    def stringify(self) -> str:
        """Retrieves file contents as a string.

        Returns:
            The internal representation of the file
            that has been read in converted to a string.
        """
        return self.__parser.stringify()

    def has(self, key: str, wild: bool = False) -> bool:
        """
        Check if a section, sub-section, or key exists.

        Some formats, like JSON, do not have sections and
        therefore, it would only be checking if a particular
        key exists.

        Args:
            key: The section, sub-section, or key to find.
            wild: Whether or not to search everywhere.

            Without `wild`, a single word `key` without a `.`
            will look at the outer most hierarchy of the file for it.

            With `wild`, that single word `key` will be searched
            for throughout the entire file.

        Returns:
            True if the key exists. False otherwise.
        """
        return self.__parser.has(key, wild=wild)

    def restore_original(
        self, original_file_path: Union[str, Path, None] = None
    ) -> None:
        """Restores the original the configuration file.

        The current one is deleted and the original is copied back
        in its place. The internal contents are then reset to the
        new file.

        Args:
            original_file_path: The original file to reset to.

            If this is not provided, it is calculated for you.
            e.g. if your configuration file is named config.json,
            this will look for aa config.original.json in the same
            directory.

        Raises:
            FileNotFoundError: If the original configuration file (whether
            calculated or passed in) does not exist.

            OSError: If the current configuration path is not writable.

            SameFileError: If current configuration path and the passed in
            original_file_path are the same file.
        """
        if original_file_path and not ConfigFilePath(original_file_path).exists():
            raise FileNotFoundError(
                f"The {original_file_path} file to restore to does not exist."
            )
        else:
            original_file_path = self.__path.original_path
            original_file_path = original_file_path.validate()

        self.__path.unlink()
        copyfile(original_file_path, self.__path)
        self.__parser.reset_internal_contents(self.__path.contents)

    def save(self) -> None:
        """
        Save your configuration changes.

        This writes the file back out, including any changes
        you've made, to the specified path given from this
        object's constructor.
        """
        with open(str(self.__path), "w") as config_file:
            config_file.write(self.stringify())
