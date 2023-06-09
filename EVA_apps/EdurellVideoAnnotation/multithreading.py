from threading import Thread

from segmentation import run_one_segmentation_job
import db_mongo

def process_video_queue(video_segmentations_queue,video_segmentation_thread,vid_id:str or None):
    if vid_id is not None and \
      vid_id not in video_segmentations_queue:
        if video_segmentation_thread is None:
            video_segmentation_thread = (vid_id,Thread(target=run_one_segmentation_job,args=(vid_id,)))
            video_segmentation_thread[1].start()
            return video_segmentation_thread
        elif video_segmentation_thread[0] != vid_id:
            if db_mongo.get_video_segmentation(video_segmentation_thread[0],raise_error=False) is not None:
                video_segmentation_thread[1].join()
                video_segmentations_queue.insert(0,vid_id)
                next_video_id = video_segmentations_queue.pop()
                video_segmentation_thread = (next_video_id,Thread(target=run_one_segmentation_job,args=(next_video_id,)))
                video_segmentation_thread[1].start()
                return video_segmentation_thread
            else:
                video_segmentations_queue.insert(0,vid_id)
                return None
    elif vid_id is None and \
      video_segmentation_thread is not None and \
      db_mongo.get_video_segmentation(video_segmentation_thread[0],raise_error=False) is not None:
        video_segmentation_thread[1].join()
        if len(video_segmentations_queue) > 0:
            next_video_id = video_segmentations_queue.pop()
            video_segmentation_thread = (next_video_id,Thread(target=run_one_segmentation_job,args=(next_video_id,)))
            video_segmentation_thread[1].start()
            return video_segmentation_thread
        return None
