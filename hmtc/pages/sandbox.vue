<template>
  <div>
    <SectionTimePanel
      :initialTime="3684125000"
      :isEditing="true"
      @updateTimes="updateTimes"
      @updateSectionTimeFromJellyfin="updateSectionTime"
    />
  </div>
</template>
<script>
export default {
  methods: {
    showMessage(message) {
      console.log(message);
    },
    updateTimes(item_id, start, end) {
      console.log("Updating times", item_id, start, end);

      const args = {
        item_id: item_id,
        start: start,
        end: end,
      };

      this.editingTime = false;
      this.timeFormDirty = false;
      this.$emit("updateTimes", args);
    },
    updateSectionTime(args) {
      console.log("Updating time from Jellyfin", args.item_id, args.time);
      this.$emit("updateSectionTime", args);
    },
  },
};
</script>
