from utils import double_sha256_digest


class MerkleTree:
    def __init__(self, digests):
        assert len(digests) > 0

        self._first = None
        self._steps_hash = None
        self._branch = None
        self._build_steps(digests)

    def _build_steps(self, digests):
        self._first = digests[0]
        # Known hashes without the first hash
        hash_list = digests[1:]
        # Ensure the correct data format
        assert all(isinstance(h, basestring) and len(h) == 32
                   for h in hash_list)
        # Number of known hashes (without the first hash)
        hash_count = len(hash_list)
        branch = []

        if hash_count > 0:
            while True:
                # Store the first hash in a list as a merkle branch step
                branch.append(hash_list[0])
                # In case when there are not a pairs of hashes to be hashed together,
                # duplicate the last one
                if not hash_count % 2:
                    hash_list.append(hash_list[-1])
                # Join and hash together all hash pairs starting from index 1 (merkle branch step)
                # and construct a new level of hashes
                hash_list = [double_sha256_digest(hash_list[i] + hash_list[i + 1])
                             for i in xrange(1, hash_count, 2)]
                hash_count = len(hash_list)
                if not hash_count:
                    break
        # Store all collected steps for further usage
        self._branch = branch

    def hash_steps(self):
        if self._steps_hash is None:
            self._steps_hash = double_sha256_digest(''.join(self._branch))
        return self._steps_hash

    def tree_digest(self, first=None):
        if first is None:
            assert len(self._first) == 32
            first = self._first

        for s in self._branch:
            first = double_sha256_digest(first + s)

        return first

    def get_merkle_branch(self):
        # Return simple copy
        return self._branch[:]
