import json
import os
import lycoris

from modules import shared, ui_extra_networks


class ExtraNetworksPageLyCORIS(ui_extra_networks.ExtraNetworksPage):
    def __init__(self, base_name='lyco', model_dir=shared.cmd_opts.lyco_dir):
        super().__init__('LyCORIS')
        self.base_name = base_name
        self.model_dir = model_dir
        self.min_model_size_mb = 1
        self.max_model_size_mb = 1e3

    def refresh_metadata(self):
        for name, lycoris_on_disk in lycoris.available_lycos.items():
            if name not in self.metadata:
                path, ext = os.path.splitext(lycoris_on_disk.filename)
                metadata_path = "".join([path, ".meta"])
                metadata = ui_extra_networks.ExtraNetworksPage.read_metadata_from_file(metadata_path)
                if metadata is not None:
                    self.metadata[name] = metadata

    def refresh(self):
        lycoris.list_available_lycos(model_dir=self.model_dir)
        self.refresh_metadata()

    def get_items_count(self):
        return len(lycoris.available_lycos)

    def list_items(self):
        for index, (name, lyco_on_disk) in enumerate(lycoris.available_lycos.items()):
            path, ext = os.path.splitext(lyco_on_disk.filename)
            search_term = self.search_terms_from_path(lyco_on_disk.filename)
            metadata = self.metadata.get(name, None)
            if metadata is not None:
                search_term = " ".join([
                    search_term,
                    ", ".join(metadata["tags"]),
                    ", ".join(metadata["trigger_word"]),
                    metadata["model_name"],
                    metadata["sha256"]])
            sort_keys = {} if 'get_sort_keys' not in dir(self) else self.get_sort_keys(lyco_on_disk.filename)
            yield {
                "name": name,
                "filename": path,
                "preview": self.find_preview(path),
                "description": self.find_description(path),
                "search_term": search_term,
                "prompt": (
                    json.dumps(f"<{self.base_name}:{name}")
                    + " + " + json.dumps(f':{shared.opts.extra_networks_default_multiplier}')
                    + " + " + json.dumps(">")
                ),
                "local_preview": f"{path}.{shared.opts.samples_format}",
                "metadata": metadata,
                "sort_keys": {'default': index, **sort_keys},
            }

    def allowed_directories_for_previews(self):
        return [self.model_dir]
