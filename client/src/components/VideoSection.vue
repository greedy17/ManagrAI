<template>
    <div class="vid-sec-container">
        <p style="font-size: 1.3rem;">{{title}}</p>
        <video controls controlsList="nodownload" :key="videoURL" style="width: 25vw;" >
            <source :src="videoURL" type="video/mp4">
        </video>
        <p><b>{{boldSubtitle}}</b> {{subtitle}}</p>
    </div>
</template>

<script>
export default {
    name: 'VideoSection',
    props: {
        title: { type: String },
        videoURL: { type: String },
        boldSubtitle: { type: String },
        subtitle: { type: String },
    }
}
</script>

<style lang="scss" scoped>
    video {
        object-fit: fill;
    }
</style>