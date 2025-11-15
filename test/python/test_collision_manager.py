import unittest
import coal
import numpy as np


class TestCollisionManager(unittest.TestCase):
    def test_dynamic_aabb_tree_collision_manager(self):
        sphere = coal.Sphere(0.5)
        sphere_obj = coal.CollisionObject(sphere)

        M_sphere = coal.Transform3s.Identity()
        M_sphere.setTranslation(np.array([-0.6, 0.0, 0.0]))
        sphere_obj.setTransform(M_sphere)

        box = coal.Box(np.array([0.5, 0.5, 0.5]))
        box_obj = coal.CollisionObject(box)

        M_box = coal.Transform3s.Identity()
        M_box.setTranslation(np.array([-0.6, 0.0, 0.0]))
        box_obj.setTransform(M_box)

        collision_manager = coal.DynamicAABBTreeCollisionManager()
        collision_manager.registerObject(sphere_obj)
        collision_manager.registerObject(box_obj)

        self.assertTrue(collision_manager.size() == 2)

        collision_manager.setup()

        # Perform collision detection
        callback = coal.CollisionCallBackDefault()
        collision_manager.collide(sphere_obj, callback)

        self.assertTrue(callback.data.result.numContacts() == 1)


if __name__ == "__main__":
    unittest.main()
