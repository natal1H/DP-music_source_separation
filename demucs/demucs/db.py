# parts taken from musdb library
# TODO: citation

import os
import numpy as np
import stempeg
from os import path as op

class Track(object):
    """
    Generic audio Track that can be wav or stem file

    Attributes
    ----------
    name : str
        Track name
    path : str
        Absolute path of mixture audio file
    stem_id : int
        stem/substream ID
    is_wav : boolean
        If stem is read from wav or mp4 stem
    subset : {'train', 'test'}
        Track belongs to which subset.
    targets : OrderedDict
        OrderedDict of mixted Targets for this ``track``.
    sources : Dict
        Dict of ``Source`` objects for this ``track``.
    chunk_start : float
        sets offset when loading the audio, defaults to 0 (beginning).
    chunk_duration : float
        sets duration for the audio, defaults to ``None`` (end).
    """

    def __init__(
        self,
        path="None",
        is_wav=False,
        stem_id=None,
        subset=None,
        chunk_start=0,
        chunk_duration=None,
        sample_rate=None
    ):
        self.path = path
        self.subset = subset
        self.stem_id = stem_id
        self.is_wav = is_wav
        self.chunk_start = chunk_start
        self.chunk_duration = chunk_duration
        self.sample_rate = sample_rate

        # load and store metadata
        if os.path.exists(self.path):
            self.info = stempeg.Info(self.path)
            self.samples = int(self.info.samples(self.stem_id))
            self.duration = self.info.duration(self.stem_id)
            self.rate = self.info.rate(self.stem_id)
        else:
            # set to `None` if no path was set (fake file)
            self.info = None
            self.samples = None
            self.duration = None
            self.rate = None

        self._audio = None

    def __len__(self):
        return self.samples

    @property
    def audio(self):
        # return cached audio if explicitly set by setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            return self.load_audio(
                self.path,
                self.stem_id,
                self.chunk_start,
                self.chunk_duration,
                self.sample_rate
            )

    @audio.setter
    def audio(self, array):
        self._audio = array

    def load_audio(
        self,
        path,
        stem_id,
        chunk_start=0,
        chunk_duration=None,
        sample_rate=None
    ):
        """array_like: [shape=(num_samples, num_channels)]
        """
        if os.path.exists(self.path):
            if self.is_wav:
                stem_id = 0
            audio, rate = stempeg.read_stems(
                filename=path,
                stem_id=stem_id,
                start=chunk_start,
                duration=chunk_duration,
                info=self.info,
                sample_rate=sample_rate,
                ffmpeg_format="s16le"
            )
            self._rate = rate
            return audio
        else:
            self._rate = None
            self._audio = None
            raise ValueError("Oops! %s cannot be loaded" % path)

    def __repr__(self):
        return "%s" % (self.path)

class MultiTrack(Track):
    def __init__(
        self,
        path=None,
        name=None,
        artist=None,
        title=None,
        sources=None,
        targets=None,
        sample_rate=None,
        *args,
        **kwargs
    ):
        super(MultiTrack, self).__init__(path=path, *args, **kwargs)

        self.name = name
        self.path = path
        try:
            split_name = name.split(' - ')
            self.artist = split_name[0]
            self.title = split_name[1]
        except IndexError:
            self.artist = artist
            self.title = title

        self.sources = sources
        self.targets = targets
        self.sample_rate = sample_rate
        self._stems = None

    @property
    def stems(self):
        """array_like: [shape=(stems, num_samples, num_channels)]
        """

        # return cached audio it explicitly set bet setter
        if self._stems is not None:
            return self._stems
        # read from disk to save RAM otherwise
        else:
            if not self.is_wav and os.path.exists(self.path):
                S, rate = stempeg.read_stems(
                    filename=self.path,
                    start=self.chunk_start,
                    duration=self.chunk_duration,
                    info=self.info,
                    sample_rate=self.sample_rate,
                    ffmpeg_format="s16le"
                )
            else:
                rate = self.rate
                S = []
                S.append(self.audio)
                # append sources in order of stem_ids
                for k, v in sorted(self.sources.items(), key=lambda x: x[1].stem_id):
                    S.append(v.audio)
                S = np.array(S)
            self._rate = rate
            return S

    def __repr__(self):
        return "%s" % (self.name)

class Source(Track):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    name : str
        Name of this source
    stem_id : int
        stem/substream ID is set here.
    is_wav : boolean
        If stem is read from wav or mp4 stem
    path : str
        Absolute path to audio file
    gain : float
        Mixing weight for this source
    """
    def __init__(
        self,
        multitrack,    # belongs to a multitrack
        name=None,     # has its own name
        path=None,     # might have its own path
        stem_id=None,  # might have its own stem_id
        gain=1.0,
        *args,
        **kwargs
    ):
        self.multitrack = multitrack
        self.name = name
        self.path = path
        self.stem_id = stem_id
        self.gain = gain
        self._audio = None

    def __repr__(self):
        return self.path

    @property
    def audio(self):
        # return cached audio if explicitly set by setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            return self.multitrack.load_audio(
                self.path,
                self.stem_id,
                self.multitrack.chunk_start,
                self.multitrack.chunk_duration,
                self.multitrack.sample_rate
            )

    @audio.setter
    def audio(self, array):
        self._audio = array

    @property
    def rate(self):
        return self.multitrack.rate

# Target Track from musdb DB mixed from several musdb Tracks
class Target(Track):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    multitrack : Track
        Track object
    sources : list[Source]
        list of ``Source`` objects for this ``Target``
    """
    def __init__(
        self,
        multitrack,
        sources,
        name=None,  # has its own name
    ):
        self.multitrack = multitrack
        self.sources = sources
        self.name = name

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]

        mixes audio for targets on the fly
        """
        mix_list = []
        for source in self.sources:
            audio = source.audio
            if audio is not None:
                mix_list.append(
                    source.gain * audio
                )
        return np.sum(np.array(mix_list), axis=0)

    @property
    def rate(self):
        return self.multitrack.rate

    def __repr__(self):
        parts = []
        for source in self.sources:
            parts.append(source.name)
        return '+'.join(parts)

class DB(object):
    """
    The musdb DB Object

    Parameters
    ----------
    root : str, optional
        musdb Root path. If set to `None` it will be read
        from the `MUSDB_PATH` environment variable

    subsets : str or list, optional
        select a _musdb_ subset `train` or `test` (defaults to both)

    is_wav : boolean, optional
        expect subfolder with wav files for each source instead stems,
        defaults to `False`

    download : boolean, optional
        download sample version of MUSDB18 which includes 7s excerpts,
        defaults to `False`

    subsets : list[str], optional
        select a _musdb_ subset `train` or `test`.
        Default `None` loads `['train', 'test']`

    split : str, optional
        when `subsets=train`, `split` selects the train/validation split.
        `split='train' loads the training split, `split='valid'` loads the validation
        split. `split=None` applies no splitting.

    Attributes
    ----------
    setup_file : str
        path to yaml file. default: `setup.yaml`
    root : str
        musdb Root path. Default is `MUSDB_PATH`. In combination with
        `download`, this path will set the download destination and set to
        '~/musdb/' by default.
    sources_dir : str
        path to Sources directory
    sources_names : list[str]
        list of names of available sources
    targets_names : list[str]
        list of names of available targets
    setup : Dict
        loaded yaml configuration
    sample_rate : Optional(Float)
        sets sample rate for optional resampling. Defaults to none
        which results in `44100.0`

    Methods
    -------
    load_mus_tracks()
        Iterates through the musdb folder structure and
        returns ``Track`` objects

    """

    def __init__(
            self,
            root=None,
            is_wav=False,
            sample_rate=None
    ):
        if sample_rate != self.setup['sample_rate']:
            self.sample_rate = sample_rate
        self.sources_names = list(self.setup['sources'].keys())
        self.targets_names = list(self.setup['targets'].keys())
        self.is_wav = is_wav
        self.tracks = self.load_mus_tracks()

    def __getitem__(self, index):
        return self.tracks[index]

    def __len__(self):
        return len(self.tracks)

    def get_track_indices_by_names(self, names):
        """Returns musdb track indices by track name

        Can be used to filter the musdb tracks for
        a validation subset by trackname

        Parameters
        == == == == ==
        names : list[str], optional
            select tracks by a given `str` or list of tracknames

        Returns
        -------
        list[int]
            return a list of ``Track`` Objects
        """
        if isinstance(names, str):
            names = [names]

        return [[t.name for t in self.tracks].index(name) for name in names]

    def load_mus_tracks(self, subsets=None, split=None):
        """Parses the musdb folder structure, returns list of `Track` objects

        Parameters
        ==========
        subsets : list[str], optional
            select a _musdb_ subset `train` or `test`.
            Default `None` loads [`train, test`].
        split : str
            for subsets='train', `split='train` applies a train/validation split.
            if `split='valid`' the validation split of the training subset will be used


        Returns
        -------
        list[Track]
            return a list of ``Track`` Objects
        """
        tracks = []

        for _, folders, files in os.walk(self.root):
            if self.is_wav:
                # parse pcm tracks and sort by name
                for track_name in sorted(folders):

                    track_folder = op.join(self.root, track_name)
                    # create new mus track
                    track = MultiTrack(
                        name=track_name,
                        path=op.join(
                            track_folder,
                            self.setup['mixture']
                        ),
                        is_wav=self.is_wav,
                        stem_id=self.setup['stem_ids']['mixture'],
                        sample_rate=self.sample_rate
                    )

                    # add sources to track
                    sources = {}
                    for src, source_file in list(
                            self.setup['sources'].items()
                    ):
                        # create source object
                        abs_path = op.join(
                            track_folder,
                            source_file
                        )
                        if os.path.exists(abs_path):
                            sources[src] = Source(
                                track,
                                name=src,
                                path=abs_path,
                                stem_id=self.setup['stem_ids'][src],
                                sample_rate=self.sample_rate
                            )
                    track.sources = sources
                    track.targets = self.create_targets(track)

                    # add track to list of tracks
                    tracks.append(track)
            else:
                # parse stem files
                for track_name in sorted(files):
                    if not track_name.endswith('.stem.mp4'):
                        continue
                    if subset == 'train':
                        if split == 'train' and track_name.split('.stem.mp4')[0] in self.setup['validation_tracks']:
                            continue
                        elif split == 'valid' and track_name.split('.stem.mp4')[0] not in self.setup[
                            'validation_tracks']:
                            continue

                    # create new mus track
                    track = MultiTrack(
                        name=track_name.split('.stem.mp4')[0],
                        path=op.join(subset_folder, track_name),
                        subset=subset,
                        stem_id=self.setup['stem_ids']['mixture'],
                        is_wav=self.is_wav,
                        sample_rate=self.sample_rate
                    )
                    # add sources to track
                    sources = {}
                    for src, source_file in list(
                            self.setup['sources'].items()
                    ):
                        # create source object
                        abs_path = op.join(
                            subset_folder,
                            track_name
                        )
                        if os.path.exists(abs_path):
                            sources[src] = Source(
                                track,
                                name=src,
                                path=abs_path,
                                stem_id=self.setup['stem_ids'][src],
                                sample_rate=self.sample_rate
                            )
                    track.sources = sources

                    # add targets to track
                    track.targets = self.create_targets(track)
                    tracks.append(track)

        return tracks

    def create_targets(self, track):
        # add targets to track
        targets = collections.OrderedDict()
        for name, target_srcs in list(
                self.setup['targets'].items()
        ):
            # add a list of target sources
            target_sources = []
            for source, gain in list(target_srcs.items()):
                if source in list(track.sources.keys()):
                    # add gain to source tracks
                    track.sources[source].gain = float(gain)
                    # add tracks to components
                    target_sources.append(track.sources[source])
                    # add sources to target
            if target_sources:
                targets[name] = Target(
                    track,
                    sources=target_sources,
                    name=name
                )

        return targets

    def save_estimates(
            self,
            user_estimates,
            track,
            estimates_dir,
            write_stems=False
    ):
        """Writes `user_estimates` to disk while recreating the musdb file structure in that folder.

        Parameters
        ==========
        user_estimates : Dict[np.array]
            the target estimates.
        track : Track,
            musdb track object
        estimates_dir : str,
            output folder name where to save the estimates.
        """
        track_estimate_dir = op.join(
            estimates_dir, track.subset, track.name
        )
        if not os.path.exists(track_estimate_dir):
            os.makedirs(track_estimate_dir)

        # write out tracks to disk
        if write_stems:
            pass
            # to be implemented
        else:
            for target, estimate in list(user_estimates.items()):
                target_path = op.join(track_estimate_dir, target + '.wav')
                stempeg.write_audio(
                    path=target_path,
                    data=estimate,
                    sample_rate=track.rate
                )

    def _check_exists(self):
        return os.path.exists(os.path.join(self.root, "train"))


